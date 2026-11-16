/* YanqhayCare: browser-native print-to-PDF reports, no external PDF service.
   The user's browser provides the Save as PDF destination in its print dialog. */
(function(global){
  'use strict';
  const escape=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  function table(headers, rows){
    const th=headers.map(x=>'<th>'+escape(x)+'</th>').join('');
    const trs=rows.map(row=>'<tr>'+row.map(c=>'<td>'+escape(c==null?'—':c)+'</td>').join('')+'</tr>').join('');
    return '<table><thead><tr>'+th+'</tr></thead><tbody>'+trs+'</tbody></table>';
  }
  function open({title,subtitle='',sections=[],at=new Date(),language='en'}){
    // Called synchronously by a user-click handler to avoid popup blocking.
    const win=global.open('','_blank');
    if(!win){global.alert(language==='es'
      ?'El navegador bloqueó la ventana del reporte. Permite ventanas emergentes y vuelve a intentar.'
      :'Your browser blocked the report window. Allow pop-ups and try again.');return false;}
    const es=language==='es';
    const body=sections.map(section=>'<section><h2>'+escape(section.title)+'</h2>'+
      (section.description?'<p class="note">'+escape(section.description)+'</p>':'')+
      (section.html||'')+
      (section.image?'<img class="plot" alt="'+escape(section.imageAlt||section.title)+'" src="'+section.image+'">':'')+
      '</section>').join('');
    const date=at instanceof Date&&Number.isFinite(at.getTime())?at:new Date();
    const html='<!doctype html><html lang="'+(es?'es':'en')+'"><head><meta charset="utf-8">'+
      '<meta name="viewport" content="width=device-width,initial-scale=1">'+
      '<title>'+escape(title)+' — YanqhayCare PDF</title><style>'+
      '@page{size:A4;margin:15mm 13mm}*{box-sizing:border-box}body{font:12px/1.48 Arial,Helvetica,sans-serif;color:#182837;margin:0;background:white}'+
      'header{padding-bottom:14px;border-bottom:2px solid #268f94;margin-bottom:15px}'+
      'h1{font-size:23px;line-height:1.15;margin:0;color:#153845}h2{font-size:15px;color:#176a70;margin:0 0 9px}'+
      'p{margin:6px 0 9px}.meta,.note{color:#526573;font-size:11px}.brand{font-weight:bold;letter-spacing:1.3px;color:#147f83;font-size:11px}'+
      'section{margin:0 0 18px;break-inside:avoid-page;page-break-inside:avoid}'+
      'table{width:100%;border-collapse:collapse;margin:7px 0 12px;font-size:10.5px;table-layout:fixed}'+
      'th,td{border-bottom:1px solid #dbe6eb;padding:6px;text-align:left;vertical-align:top;overflow-wrap:anywhere}th{background:#eef6f6;color:#244653}'+
      '.plot{display:block;width:100%;max-height:230px;object-fit:contain;border:1px solid #dce6ea;margin:8px auto}'+
      '.foot{border-top:1px solid #ccd9df;margin-top:18px;padding-top:9px;color:#536672;font-size:10px}'+
      '.tools{display:flex;gap:10px;align-items:center;margin:0 0 20px;padding:13px;background:#eef5f6;border-radius:9px}'+
      '.tools button{border:0;background:#167b81;color:white;font:700 13px Arial;padding:11px 17px;border-radius:8px;cursor:pointer}'+
      '@media print{.tools{display:none}section{break-inside:avoid-page}}'+
      '</style></head><body>'+
      '<div class="tools"><button onclick="window.print()">'+(es?'Guardar como PDF / Imprimir':'Save as PDF / Print')+'</button>'+
      '<span>'+(es?'En el destino de impresión, selecciona "Guardar como PDF".':'Choose "Save as PDF" in the print destination.')+'</span></div>'+
      '<header><div class="brand">YANQHAYCARE</div><h1>'+escape(title)+'</h1>'+
      (subtitle?'<p>'+escape(subtitle)+'</p>':'')+
      '<p class="meta">'+(es?'Reporte generado':'Report generated')+': '+escape(date.toLocaleString(es?'es-PE':'en-US'))+'</p></header>'+
      body+'<div class="foot">'+(es
        ?'Prototipo de investigación. Los resultados derivados de cámara son experimentales; no constituyen diagnóstico médico ni mediciones clínicas validadas.'
        :'Research prototype. Camera-derived outputs are experimental and are not a medical diagnosis or clinically validated measurements.')+
      '</div></body></html>';
    win.document.open();win.document.write(html);win.document.close();win.focus();
    return true;
  }
  global.YanqhayPDF={open,table,escape};
})(window);
