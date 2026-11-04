def lum(h):
    h=h.lstrip('#'); c=[int(h[i:i+2],16)/255 for i in (0,2,4)]
    c=[x/12.92 if x<=0.03928 else ((x+0.055)/1.055)**2.4 for x in c]
    return 0.2126*c[0]+0.7152*c[1]+0.0722*c[2]
def cr(a,b):
    la,lb=sorted([lum(a),lum(b)],reverse=True); return (la+0.05)/(lb+0.05)
pairs = {
 # claro
 "texto primário / fundo":("#0F172A","#FFFFFF"), "texto primário / fundo-sutil":("#0F172A","#F5F7FA"),
 "texto secundário / fundo":("#475569","#FFFFFF"), "texto secundário / fundo-sutil":("#475569","#F5F7FA"),
 "texto terciário / fundo":("#64748B","#FFFFFF"),
 "ação primária (texto branco)":("#FFFFFF","#1D4ED8"), "ação hover (texto branco)":("#FFFFFF","#1E40AF"),
 "link / fundo":("#1D4ED8","#FFFFFF"), "marca navy (texto branco)":("#FFFFFF","#10243E"),
 "índigo destaque / fundo":("#3730D9","#FFFFFF"),
 "sucesso texto / tint":("#166534","#DCFCE7"), "alerta texto / tint":("#92400E","#FEF3C7"),
 "perigo texto / tint":("#991B1B","#FEE2E2"), "info texto / tint":("#075985","#E0F2FE"),
 "reservado texto / tint":("#5B21B6","#EDE9FE"), "conferência texto / tint":("#115E59","#CCFBF1"),
 "baixado texto / tint":("#334155","#E2E8F0"), "emprestado texto / tint":("#1E40AF","#DBEAFE"),
 "perigo botão (texto branco)":("#FFFFFF","#B91C1C"),
 "borda de controle / fundo (3:1)":("#64748B","#FFFFFF"), "anel de foco / fundo (3:1)":("#2563EB","#FFFFFF"),
 # escuro
 "E texto primário / fundo":("#E6EBF2","#0B1220"), "E texto secundário / superfície":("#A7B3C4","#111A2B"),
 "E ação primária (texto escuro)":("#0B1220","#60A5FA"), "E link / fundo":("#60A5FA","#0B1220"),
 "E sucesso texto / superfície":("#4ADE80","#111A2B"), "E alerta texto / superfície":("#FBBF24","#111A2B"),
 "E perigo texto / superfície":("#F87171","#111A2B"), "E foco / fundo":("#93C5FD","#0B1220"),
 "E borda de controle / superfície (3:1)":("#64748B","#111A2B"),
}
for k,(a,b) in pairs.items():
    r=cr(a,b); need=3.0 if "3:1" in k else 4.5
    print(f"{'OK ' if r>=need else 'FALHA'} {r:5.2f}:1 (mín {need})  {k}  {a} sobre {b}")
