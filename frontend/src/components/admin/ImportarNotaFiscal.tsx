'use client';

import { useState } from 'react';
import { ApiError, cadastrarItem, extrairProdutosPDF, registrarNotaFiscal, type Setor } from '@/lib/api';

type ProdutoNFe = { codigo: string; nome: string; quantidade: number; unidade: string; valorUnitario: number; valorTotal: number };

function textoNoElemento(parent: Element, nome: string): string {
  const elemento = Array.from(parent.getElementsByTagName('*')).find((node) => node.localName === nome);
  return elemento?.textContent?.trim() || '';
}

function lerXMLNFe(xml: string): ProdutoNFe[] {
  const doc = new DOMParser().parseFromString(xml, 'application/xml');
  if (doc.querySelector('parsererror')) throw new Error('O arquivo XML está inválido ou corrompido.');
  const detalhes = Array.from(doc.getElementsByTagName('*')).filter((node) => node.localName === 'det');
  if (!detalhes.length) throw new Error('Não encontrei produtos nesse XML. Envie o XML de uma NF-e (modelo 55).');
  return detalhes.map((det, index) => {
    const produto = Array.from(det.getElementsByTagName('*')).find((node) => node.localName === 'prod');
    if (!produto) throw new Error(`Produto ${index + 1}: estrutura XML inesperada.`);
    const get = (nome: string) => textoNoElemento(produto, nome);
    const codigo = get('cProd');
    const nome = get('xProd');
    const quantidade = Number(get('qCom').replace(',', '.'));
    const valorUnitario = Number(get('vUnCom').replace(',', '.')) || 0;
    const valorTotal = Number(get('vProd').replace(',', '.')) || 0;
    if (!nome || !Number.isFinite(quantidade) || quantidade <= 0) throw new Error(`Produto ${index + 1}: nome ou quantidade inválida.`);
    return { codigo, nome, quantidade: Math.max(1, Math.round(quantidade)), unidade: get('uCom'), valorUnitario, valorTotal };
  });
}

export default function ImportarNotaFiscal({ setores, onImportado }: { setores: Setor[]; onImportado: () => void }) {
  const [arquivo, setArquivo] = useState('');
  const [visualUrl, setVisualUrl] = useState<string | null>(null);
  const [tipoVisual, setTipoVisual] = useState<'pdf' | 'imagem' | null>(null);
  const [produtos, setProdutos] = useState<ProdutoNFe[]>([]);
  const [setorId, setSetorId] = useState('');
  const [area, setArea] = useState('Almoxarifado');
  const [erro, setErro] = useState('');
  const [aviso, setAviso] = useState('');
  const [importando, setImportando] = useState(false);
  const [tipoArquivo, setTipoArquivo] = useState('XML');

  async function selecionarArquivo(file?: File) {
    setErro(''); setAviso(''); setProdutos([]); setVisualUrl(null); setTipoVisual(null);
    if (!file) return;
    setArquivo(file.name);
    try {
      if (file.type === 'application/pdf' || file.name.toLowerCase().endsWith('.pdf')) { setTipoArquivo('PDF'); setVisualUrl(URL.createObjectURL(file)); setTipoVisual('pdf'); setAviso('Analisando o PDF para extrair os produtos. Revise cuidadosamente os dados antes de importar.'); const resposta = await extrairProdutosPDF(file); setProdutos(resposta.produtos); setAviso(`${resposta.produtos.length} produto(s) extraído(s) do PDF. ${resposta.aviso}`); return; }
      if (file.type.startsWith('image/')) { setTipoArquivo('IMAGEM'); setVisualUrl(URL.createObjectURL(file)); setTipoVisual('imagem'); setAviso('Imagem carregada para visualização. Para extração automática de produtos, utilize o PDF ou XML da nota fiscal.'); return; }
      if (!file.name.toLowerCase().endsWith('.xml')) throw new Error('Formato não suportado. Envie XML, PDF ou imagem da nota fiscal.');
      setTipoArquivo('XML');
      const xml = await file.text();
      const encontrados = lerXMLNFe(xml);
      setProdutos(encontrados);
      setAviso(`${encontrados.length} produto(s) extraído(s) do XML. Revise os dados e escolha o setor antes de importar.`);
    } catch (e) { setErro(e instanceof Error ? e.message : 'Não foi possível ler a nota fiscal.'); }
  }

  async function importar() {
    if (!produtos.length || !setorId) { setErro('Selecione um setor para os produtos antes de importar.'); return; }
    setImportando(true); setErro(''); setAviso('');
    let sucesso = 0;
    const falhas: string[] = [];
    for (const produto of produtos) {
      try {
        await cadastrarItem({
          nome: produto.nome.slice(0, 150),
          patrimonio: produto.codigo ? produto.codigo.slice(0, 50) : undefined,
          codigo_qr: produto.codigo ? `NFE-${produto.codigo}`.slice(0, 120) : undefined,
          area: area.trim() || undefined,
          setor_id: Number(setorId),
          quantidade_total: produto.quantidade,
        });
        sucesso += 1;
      } catch (e) {
        const mensagem = e instanceof ApiError ? e.message : 'erro desconhecido';
        falhas.push(`${produto.nome}: ${mensagem}`);
      }
    }
    setImportando(false);
    try { await registrarNotaFiscal({ nome_arquivo: arquivo, tipo_arquivo: tipoArquivo, produtos, total_cadastrados: sucesso, observacoes: falhas.join(' | ').slice(0, 2000) }); } catch (e) { setErro(`Os itens foram processados, mas não foi possível gravar a nota no histórico: ${e instanceof Error ? e.message : 'erro desconhecido'}`); }
    onImportado();
    setAviso(`Importação finalizada: ${sucesso} produto(s) cadastrado(s) com as quantidades da nota.`);
    if (falhas.length) setErro(`${falhas.length} produto(s) não foram importados. ${falhas.slice(0, 4).join(' | ')}`);
  }

  return <section className="invoice-panel rounded-2xl border border-slate-200 bg-white p-5 shadow-sm sm:p-6">
    <div className="invoice-heading mb-5">
      <div className="invoice-heading-icon" aria-hidden="true">▤</div>
      <div><p className="text-xs font-bold uppercase tracking-widest text-indigo-700">Entrada por documento</p><h2 className="mt-1 text-xl font-bold text-slate-900">Importar nota fiscal</h2><p className="mt-1 text-sm text-slate-500">Envie o documento, confira os produtos encontrados e registre a entrada no estoque.</p></div>
    </div>
    <label className="invoice-dropzone flex cursor-pointer flex-col items-center justify-center rounded-xl border-2 border-dashed border-slate-300 bg-slate-50 px-5 py-8 text-center hover:border-indigo-400 hover:bg-indigo-50/40">
      <span className="invoice-upload-icon" aria-hidden="true"><svg viewBox="0 0 24 24" width="28" height="28" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"><path d="M12 16V4m-5 5 5-5 5 5"/><path d="M5 15v4a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1v-4"/></svg></span>
      <span className="mt-3 font-semibold text-slate-800">{arquivo || 'Solte sua nota fiscal aqui'}</span>
      <span className="mt-1 text-sm text-slate-600"><span className="font-semibold text-indigo-700">Clique para procurar</span> no dispositivo</span>
      <span className="mt-2 text-xs text-slate-500">XML ou PDF para extrair produtos · imagem para visualizar</span>
      <input type="file" accept=".xml,application/xml,text/xml,application/pdf,image/*" className="sr-only" onChange={(e) => void selecionarArquivo(e.target.files?.[0])} />
    </label>
    {arquivo && <p className="invoice-file-label mt-3 text-xs text-slate-500"><span aria-hidden="true">✓</span> Arquivo selecionado: <strong>{arquivo}</strong></p>}
    {visualUrl && <div className="mt-4 overflow-hidden rounded-xl border border-slate-200 bg-slate-50"><div className="border-b border-slate-200 px-3 py-2 text-sm font-semibold text-slate-700">Pré-visualização do documento</div>{tipoVisual === 'pdf' ? <iframe title="Pré-visualização da nota fiscal" src={visualUrl} className="h-[520px] w-full bg-white" /> : <img src={visualUrl} alt="Nota fiscal enviada" className="max-h-[520px] w-full object-contain" />}</div>}
    {erro && <div role="alert" className="mt-3 rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-800">{erro}</div>}
    {aviso && <div role="status" className="mt-3 rounded-lg border border-emerald-200 bg-emerald-50 p-3 text-sm text-emerald-800">{aviso}</div>}
    {produtos.length > 0 && <>
      <div className="mt-4 grid gap-3 sm:grid-cols-2"><label className="text-sm font-semibold text-slate-700">Setor de destino<select value={setorId} onChange={(e) => setSetorId(e.target.value)} className="mt-1 w-full rounded-lg border border-slate-300 bg-white p-3 font-normal"><option value="">Selecione o setor…</option>{setores.map((s) => <option key={s.id} value={s.id}>{s.nome}</option>)}</select></label><label className="text-sm font-semibold text-slate-700">Área<input value={area} onChange={(e) => setArea(e.target.value)} className="mt-1 w-full rounded-lg border border-slate-300 p-3 font-normal" /></label></div>
      <div className="invoice-results-title mt-5"><strong>Produtos encontrados ({produtos.length})</strong><span>Revise antes de importar</span></div><div className="mt-3 overflow-x-auto rounded-lg border border-slate-200"><table className="min-w-full text-left text-sm"><thead className="bg-slate-50 text-xs uppercase text-slate-500"><tr><th className="p-3">Código</th><th className="p-3">Produto</th><th className="p-3">Qtd.</th><th className="p-3">Valor total</th></tr></thead><tbody>{produtos.map((p, i) => <tr key={`${p.codigo}-${i}`} className="border-t border-slate-100"><td className="p-3 font-mono text-xs">{p.codigo || '—'}</td><td className="p-3 font-medium text-slate-800">{p.nome}<div className="text-xs text-slate-400">Unidade: {p.unidade || '—'}</div></td><td className="p-3">{p.quantidade}</td><td className="p-3">{p.valorTotal.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}</td></tr>)}</tbody></table></div>
      <button disabled={importando || !setorId} onClick={() => void importar()} className="mt-4 w-full rounded-lg bg-indigo-700 px-4 py-3 font-bold text-white hover:bg-indigo-800 disabled:cursor-not-allowed disabled:opacity-50">{importando ? 'Importando produtos…' : `Cadastrar ${produtos.length} produto(s) no estoque`}</button>
      <p className="mt-2 text-xs text-slate-500">A quantidade da NF-e será usada como estoque inicial. Produtos já existentes ou com códigos duplicados podem ser rejeitados e aparecerão no relatório de erros.</p>
    </>}
  </section>;
}
