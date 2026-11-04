'use client';

import { useCallback, useEffect, useRef, useState } from 'react';
import { ApiError, escanearQR, type Setor, type QRScanResponse } from '@/lib/api';

type CameraOption = { deviceId: string; label: string };
type DetectedBarcode = { rawValue: string };
type BarcodeDetectorLike = { detect: (source: HTMLVideoElement) => Promise<DetectedBarcode[]> };
type BarcodeDetectorConstructor = new (options?: { formats: string[] }) => BarcodeDetectorLike;

export default function LeitorQRAlmoxarifado({
  setores: _setores,
  onItemCadastrado,
}: {
  setores: Setor[];
  onItemCadastrado: () => void;
}) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const detectorRef = useRef<BarcodeDetectorLike | null>(null);
  const processandoRef = useRef(false);
  const identidadeRef = useRef<string | null>(null);
  const ausenciasRef = useRef(0);
  const [cameras, setCameras] = useState<CameraOption[]>([]);
  const [cameraId, setCameraId] = useState('');
  const [ativo, setAtivo] = useState(false);
  const [processando, setProcessando] = useState(false);
  const [resultado, setResultado] = useState<QRScanResponse | null>(null);
  const [amostra, setAmostra] = useState<string | null>(null);
  const [erro, setErro] = useState<string | null>(null);
  const [eventos, setEventos] = useState<Array<{ id: number; hora: string; tipo: 'ok' | 'erro' | 'info'; texto: string }>>([]);
  const eventoIdRef = useRef(0);
  const [aviso, setAviso] = useState<{ tipo: 'ok' | 'erro'; texto: string } | null>(null);
  const [aguardandoLiberacao, setAguardandoLiberacao] = useState(false);
  const avisoTimerRef = useRef<number | null>(null);

  const mostrarAviso = useCallback((tipo: 'ok' | 'erro', texto: string) => {
    if (avisoTimerRef.current) window.clearTimeout(avisoTimerRef.current);
    setAviso({ tipo, texto });
    avisoTimerRef.current = window.setTimeout(() => setAviso(null), 5000);
  }, []);

  const registrarEvento = useCallback((tipo: 'ok' | 'erro' | 'info', texto: string) => {
    const hora = new Date().toLocaleTimeString('pt-BR');
    setEventos((anteriores) => [{ id: ++eventoIdRef.current, hora, tipo, texto }, ...anteriores].slice(0, 12));
  }, []);

  const pararCamera = useCallback(() => {
    streamRef.current?.getTracks().forEach((track) => track.stop());
    streamRef.current = null;
    if (videoRef.current) videoRef.current.srcObject = null;
    setAtivo(false);
  }, []);

  const carregarCameras = useCallback(async () => {
    if (!navigator.mediaDevices?.enumerateDevices) return;
    try {
      const devices = await navigator.mediaDevices.enumerateDevices();
      const lista = devices.filter((d) => d.kind === 'videoinput').map((d, i) => ({
        deviceId: d.deviceId,
        label: d.label || `Câmera ${i + 1}`,
      }));
      setCameras(lista);
      if (!cameraId && lista.length) {
        const preferida = lista.find((d) => /back|rear|environment|traseira/i.test(d.label)) || lista[0];
        setCameraId(preferida.deviceId);
      }
    } catch {
      registrarEvento('erro', 'Não foi possível listar as câmeras disponíveis.');
    }
  }, [cameraId, registrarEvento]);

  async function iniciarCamera() {
    setErro(null);
    pararCamera();
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: {
          width: { ideal: 1280 }, height: { ideal: 720 },
          ...(cameraId ? { deviceId: { exact: cameraId } } : { facingMode: { ideal: 'environment' } }),
        },
        audio: false,
      });
      streamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        await videoRef.current.play();
      }
      const BarcodeDetector = (window as unknown as { BarcodeDetector?: BarcodeDetectorConstructor }).BarcodeDetector;
      detectorRef.current = BarcodeDetector ? new BarcodeDetector({ formats: ['qr_code'] }) : null;
      identidadeRef.current = null;
      ausenciasRef.current = 0;
      setAguardandoLiberacao(false);
      setResultado(null);
      setAmostra(null);
      setAtivo(true);
      await carregarCameras();
      registrarEvento('info', detectorRef.current
        ? 'Câmera pronta; detecção local de QR ativada.'
        : 'Câmera pronta; este navegador não oferece detecção local de QR.');
    } catch (e) {
      const mensagem = e instanceof Error ? e.message : 'Verifique a permissão e a conexão da câmera.';
      setErro(`Não foi possível abrir a câmera. ${mensagem}`);
      registrarEvento('erro', `Falha ao abrir câmera: ${mensagem}`);
    }
  }

  const capturarERegistrar = useCallback(async () => {
    const video = videoRef.current;
    const canvas = canvasRef.current;
    if (!video || !canvas || processandoRef.current || !ativo || video.readyState < 2 || !video.videoWidth) return;

    // Em navegadores compatíveis, só envia a imagem ao backend quando um QR novo é
    // detectado localmente. Assim o mesmo QR parado na câmera não incrementa o estoque repetidamente.
    if (detectorRef.current) {
      try {
        const codigos = await detectorRef.current.detect(video);
        if (!codigos.length) {
          ausenciasRef.current += 1;
          if (ausenciasRef.current >= 3) identidadeRef.current = null;
          return;
        }
        ausenciasRef.current = 0;
        const identidadeDetectada = codigos[0].rawValue;
        if (!identidadeDetectada || identidadeDetectada === identidadeRef.current) return;
        identidadeRef.current = identidadeDetectada;
      } catch {
        // Falhas transitórias do detector local não derrubam a câmera.
        return;
      }
    } else if (identidadeRef.current) {
      // Fallback seguro: sem detector local, aguarda liberação explícita ("Ler próximo item")
      // para evitar contagem duplicada do mesmo QR parado na câmera.
      return;
    }

    const maxW = 1280;
    const scale = Math.min(1, maxW / video.videoWidth);
    canvas.width = Math.round(video.videoWidth * scale);
    canvas.height = Math.round(video.videoHeight * scale);
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    const amostraVisual = canvas.toDataURL('image/jpeg', 0.82);
    processandoRef.current = true;
    setProcessando(true);
    try {
      const blob = await new Promise<Blob | null>((resolve) => canvas.toBlob(resolve, 'image/jpeg', 0.82));
      if (!blob) throw new Error('Não foi possível preparar a imagem da câmera.');
      const leitura = await escanearQR(blob);
      if (!leitura.sucesso) {
        // O servidor respondeu OK, mas não achou QR na imagem: nada foi gravado.
        // Sem detector local isso acontece a cada tentativa; fica em silêncio para não poluir o registro.
        if (detectorRef.current) {
          setErro(leitura.mensagem);
          registrarEvento('info', leitura.mensagem);
        }
        return;
      }
      setAmostra(amostraVisual);
      // Houve gravação no estoque: bloqueia novas leituras do mesmo QR até ele sair da câmera
      // (com detector) ou até o usuário liberar manualmente (sem detector).
      if (!detectorRef.current) {
        identidadeRef.current = leitura.raw || leitura.codigo_qr || '__lido__';
        setAguardandoLiberacao(true);
      }
      setResultado(leitura);
      setErro(null);
      const nomeItem = leitura.item?.nome || leitura.nome || leitura.codigo_qr || 'item reconhecido';
      const textoOk = `${leitura.acao === 'cadastrado' ? 'Cadastrado' : 'Estoque +1'}: ${nomeItem}`;
      registrarEvento('ok', textoOk);
      mostrarAviso('ok', textoOk);
      onItemCadastrado();
    } catch (e) {
      const status = e instanceof ApiError ? e.status : 0;
      const mensagem = e instanceof ApiError ? e.message : (e instanceof Error ? e.message : 'Erro inesperado na leitura.');
      // Não libera o QR para nova tentativa automática: se o servidor gravou antes de falhar,
      // reenviar o mesmo QR a cada 350 ms somaria +1 repetidamente no estoque.
      if (!identidadeRef.current) identidadeRef.current = '__erro__';
      if (!detectorRef.current) setAguardandoLiberacao(true);
      setErro(mensagem);
      registrarEvento('erro', mensagem);
      mostrarAviso('erro', mensagem);
      // Em erro de servidor/rede o estado real é incerto: atualiza a lista para refletir o banco.
      if (status === 0 || status >= 500) onItemCadastrado();
    } finally {
      processandoRef.current = false;
      setProcessando(false);
    }
  }, [ativo, onItemCadastrado, registrarEvento, mostrarAviso]);

  useEffect(() => { void carregarCameras(); }, [carregarCameras]);
  useEffect(() => {
    if (!ativo) return;
    const timer = window.setInterval(() => { void capturarERegistrar(); }, detectorRef.current ? 350 : 800);
    return () => window.clearInterval(timer);
  }, [ativo, capturarERegistrar]);
  useEffect(() => () => {
    streamRef.current?.getTracks().forEach((track) => track.stop());
    if (avisoTimerRef.current) window.clearTimeout(avisoTimerRef.current);
  }, []);

  function liberarProximaLeitura() {
    identidadeRef.current = null;
    ausenciasRef.current = 0;
    setAguardandoLiberacao(false);
    setErro(null);
    registrarEvento('info', 'Pronto para ler o próximo item.');
  }

  return (
    <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm sm:p-6">
      {aviso && (
        <div
          role="status"
          aria-live="polite"
          className={`fixed right-4 top-4 z-50 max-w-sm rounded-xl px-5 py-4 text-sm font-semibold text-white shadow-2xl ${aviso.tipo === 'ok' ? 'bg-emerald-600' : 'bg-red-600'}`}
        >
          {aviso.tipo === 'ok' ? '✓ ' : '✕ '}{aviso.texto}
        </div>
      )}
      <div className="mb-5 flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
        <div>
          <p className="text-xs font-bold uppercase tracking-widest text-blue-700">Visão computacional</p>
          <h2 className="mt-1 text-xl font-bold text-slate-900">Entrada automática por QR Code</h2>
          <p className="mt-1 max-w-2xl text-sm text-slate-500">A câmera lê o QR e o sistema cadastra o item novo ou adiciona uma unidade ao item existente.</p>
        </div>
        <div className="flex gap-2">
          {!ativo ? <button onClick={() => void iniciarCamera()} className="rounded-lg bg-blue-700 px-4 py-2.5 font-semibold text-white hover:bg-blue-800">Abrir câmera</button>
            : <button onClick={pararCamera} className="rounded-lg bg-red-600 px-4 py-2.5 font-semibold text-white hover:bg-red-700">Parar câmera</button>}
        </div>
      </div>

      <div className="mb-4 grid gap-3 sm:grid-cols-[1fr_auto] sm:items-end">
        <label className="block text-sm font-semibold text-slate-700">Câmera utilizada
          <select value={cameraId} onChange={(e) => setCameraId(e.target.value)} disabled={ativo} className="mt-1 block w-full rounded-lg border border-slate-300 bg-white p-3 font-normal disabled:bg-slate-100">
            {cameras.length === 0 && <option value="">Câmera padrão do dispositivo</option>}
            {cameras.map((camera, i) => <option key={camera.deviceId || i} value={camera.deviceId}>{camera.label}</option>)}
          </select>
        </label>
        <button onClick={() => void carregarCameras()} type="button" className="rounded-lg border border-slate-300 px-3 py-3 text-sm font-semibold text-slate-700 hover:bg-slate-50">Atualizar lista</button>
      </div>

      <div className="grid gap-5 xl:grid-cols-[minmax(0,1.6fr)_minmax(260px,1fr)]">
        <div>
          <div className="relative mx-auto aspect-video max-w-3xl overflow-hidden rounded-xl bg-slate-950 ring-1 ring-slate-200">
            <video ref={videoRef} autoPlay muted playsInline className="h-full w-full object-cover" />
            <div className="pointer-events-none absolute left-[20%] top-[15%] h-[70%] w-[60%] rounded-xl border-2 border-emerald-400 shadow-[0_0_0_9999px_rgba(0,0,0,.32)]" />
            {!ativo && <div className="absolute inset-0 flex flex-col items-center justify-center gap-2 px-5 text-center text-white"><span className="text-3xl">▦</span><span className="text-sm">Selecione a câmera e clique em “Abrir câmera”.</span></div>}
            {processando && <div className="absolute bottom-3 left-1/2 -translate-x-1/2 rounded-full bg-white px-3 py-1.5 text-xs font-bold text-slate-800 shadow">Processando leitura…</div>}
            {ativo && !processando && <div className="absolute bottom-3 left-3 rounded-full bg-emerald-500/95 px-3 py-1 text-xs font-bold text-white">● Câmera ativa</div>}
          </div>
          <canvas ref={canvasRef} className="hidden" />
          {aguardandoLiberacao && ativo && (
            <button type="button" onClick={liberarProximaLeitura} className="mt-3 w-full rounded-lg bg-slate-800 px-4 py-3 font-semibold text-white hover:bg-slate-900">
              Ler próximo item
            </button>
          )}
          {erro && <div role="alert" className="mt-3 rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-800"><b>Falha na leitura</b><p className="mt-1">{erro}</p></div>}
          {resultado && <div role="status" className={`mt-3 rounded-xl border p-4 ${resultado.acao === 'cadastrado' ? 'border-emerald-200 bg-emerald-50' : 'border-blue-200 bg-blue-50'}`}>
            <p className="font-bold text-slate-900">{resultado.acao === 'cadastrado' ? '✓ Item cadastrado automaticamente' : '✓ Unidade adicionada ao estoque'}</p>
            <p className="mt-1 text-sm text-slate-700">{resultado.mensagem}</p>
            {resultado.item && <div className="mt-3 grid grid-cols-2 gap-2 text-sm"><div><span className="text-slate-500">Item</span><p className="font-semibold">{resultado.item.nome}</p></div><div><span className="text-slate-500">Patrimônio</span><p className="font-semibold">{resultado.item.patrimonio || '—'}</p></div><div><span className="text-slate-500">Disponíveis</span><p className="font-semibold">{resultado.item.quantidade_disponivel}</p></div><div><span className="text-slate-500">Estoque total</span><p className="font-semibold">{resultado.item.quantidade_total}</p></div></div>}
          </div>}
        </div>

        <aside className="space-y-4">
          <div className="rounded-xl border border-slate-200 p-4">
            <div className="mb-3 flex items-center justify-between"><h3 className="font-bold text-slate-800">Amostra da leitura</h3>{amostra && <span className="rounded-full bg-emerald-100 px-2 py-1 text-xs font-bold text-emerald-800">Registrada</span>}</div>
            {amostra ? <img src={amostra} alt="Imagem capturada no momento da leitura do QR Code" className="aspect-video w-full rounded-lg bg-slate-100 object-contain" /> : <div className="flex aspect-video items-center justify-center rounded-lg bg-slate-50 px-4 text-center text-sm text-slate-400">A captura da leitura aparecerá aqui após um QR ser processado.</div>}
            <p className="mt-2 text-xs text-slate-500">Evidência visual da captura que gerou o cadastro/entrada.</p>
          </div>
          <div className="rounded-xl border border-slate-200 p-4">
            <div className="mb-3 flex items-center justify-between"><h3 className="font-bold text-slate-800">Registro de atividade</h3><span className="text-xs text-slate-500">Últimos 12 eventos</span></div>
            {eventos.length === 0 ? <p className="text-sm text-slate-400">Aguardando atividade da câmera…</p> : <ul className="space-y-2">{eventos.map((evento) => <li key={evento.id} className="flex gap-2 text-sm"><span className="shrink-0 font-mono text-xs text-slate-400">{evento.hora}</span><span className={evento.tipo === 'erro' ? 'text-red-700' : evento.tipo === 'ok' ? 'text-emerald-700' : 'text-slate-600'}>{evento.tipo === 'erro' ? '✕ ' : evento.tipo === 'ok' ? '✓ ' : '• '}{evento.texto}</span></li>)}</ul>}
          </div>
          {!detectorRef.current && ativo && <p className="rounded-lg bg-amber-50 p-3 text-xs text-amber-800">Este navegador não oferece detecção local de QR. Para evitar entradas duplicadas, após cada leitura clique em “Ler próximo item” antes de ler o próximo. Recomendado: Chrome ou Edge atualizados.</p>}
        </aside>
      </div>
      <p className="mt-4 text-xs text-slate-500">Dica: mantenha o QR inteiro dentro do retângulo verde e aguarde a confirmação antes de retirar o item.</p>
    </section>
  );
}
