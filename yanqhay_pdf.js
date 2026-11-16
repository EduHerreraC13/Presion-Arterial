/* YanqhayCare browser-only PDF reports. No third-party PDF library or upload.
   Rasterized A4 pages at 150 dpi preserve charts captured from real result canvases. */
(function () {
  'use strict';
  const WIDTH=1240, HEIGHT=1754, LEFT=82, RIGHT=WIDTH-82, TOP=104, BOTTOM=HEIGHT-108;
  const enc = new TextEncoder();
  const bytes = str => enc.encode(str);
  const norm = value => String(value == null ? '—' : value);
  const cleanFile = name => norm(name).replace(/[^a-zA-Z0-9._-]+/g,'_').slice(0,100)+'.pdf';

  function reportPages(report) {
    const pages=[];
    let canvas,ctx,y;
    function page(){
      canvas=document.createElement('canvas');canvas.width=WIDTH;canvas.height=HEIGHT;
      ctx=canvas.getContext('2d');
      ctx.fillStyle='#ffffff';ctx.fillRect(0,0,WIDTH,HEIGHT);
      ctx.fillStyle='#0e3540';ctx.fillRect(0,0,WIDTH,18);
      ctx.fillStyle='#74858f';ctx.font='20px Arial, sans-serif';
      ctx.fillText('YanqhayCare  |  Camera-based research report',LEFT,HEIGHT-58);
      ctx.fillText('Page '+(pages.length+1),RIGHT-95,HEIGHT-58);
      y=TOP;
    }
    function save(){
      pages.push(canvas.toDataURL('image/jpeg',0.88));
    }
    function ensure(height) {
      if (y+height>BOTTOM){save();page();}
    }
    function textLine(str,fontSize=26,color='#233b47',bold=false,indent=0) {
      const content=norm(str);
      ctx.font=(bold?'bold ':'')+fontSize+'px Arial, sans-serif';
      const max=RIGHT-LEFT-indent;
      const words=content.split(/\s+/);
      let line='';
      function flush() {
        ensure(fontSize+14);
        ctx.font=(bold?'bold ':'')+fontSize+'px Arial, sans-serif';
        ctx.fillStyle=color;ctx.fillText(line || ' ',LEFT+indent,y);
        y+=fontSize+13;
      }
      for(const word of words) {
        const candidate=line?line+' '+word:word;
        if(ctx.measureText(candidate).width>max && line) {flush();line=word;}
        else line=candidate;
      }
      if(line)flush();
    }
    function heading(str) {
      ensure(87);y+=22;
      ctx.fillStyle='#14776e';ctx.fillRect(LEFT,y-26,6,38);
      textLine(str,31,'#0e3540',true,20);
      y+=13;
    }
    function picture(data, label) {
      if(!data)return;
      if(label)textLine(label,23,'#315867',true);
      const img=new Image();img.src=data;
      const w=RIGHT-LEFT;
      const intrinsicW=img.naturalWidth||1100,intrinsicH=img.naturalHeight||220;
      const h=Math.min(490,w*intrinsicH/intrinsicW);
      ensure(h+40);
      ctx.fillStyle='#edf3f3';ctx.fillRect(LEFT,y,w,h+12);
      ctx.drawImage(img,LEFT,y,w,h);y+=h+32;
    }
    page();
    textLine(report.title||'Monitoring report',43,'#0e3540',true);
    textLine('Generated: '+new Date().toLocaleString(),22,'#49636f');
    if(report.subtitle)textLine(report.subtitle,24,'#49636f');
    y+=30;
    for(const section of (report.sections||[])){
      if(section.heading)heading(section.heading);
      for(const line of (section.lines||[]))textLine(line,24,'#263a44',false,9);
      if(section.image)picture(section.image,section.imageLabel||'');
      y+=9;
    }
    heading('Interpretation');
    textLine(report.disclaimer||'Research prototype only. Camera-derived indicators are experimental and are not medical measurements or diagnoses.',21,'#4a6470');
    save();
    return pages;
  }

  function assemble(pages){
    const parts=[];let position=0;const offsets=[0];
    const append=a=>{parts.push(a);position+=a.length;};
    const obj=(id,content)=>{offsets[id]=position;append(bytes(id+' 0 obj\n'+content+'\nendobj\n'));};
    append(bytes('%PDF-1.4\n%YanqhayCare\n'));
    obj(1,'<< /Type /Catalog /Pages 2 0 R >>');
    const refs=pages.map((_,i)=> (3+i*3)+' 0 R').join(' ');
    obj(2,'<< /Type /Pages /Kids ['+refs+'] /Count '+pages.length+' >>');
    for(let i=0;i<pages.length;i++){
      const pageId=3+i*3, imageId=pageId+1, contentId=pageId+2;
      obj(pageId,'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595.28 841.89] /Resources << /XObject << /Im0 '+imageId+' 0 R >> >> /Contents '+contentId+' 0 R >>');
      const raw=atob(pages[i].split(',')[1]),jpeg=new Uint8Array(raw.length);
      for(let j=0;j<raw.length;j++)jpeg[j]=raw.charCodeAt(j);
      offsets[imageId]=position;
      append(bytes(imageId+' 0 obj\n<< /Type /XObject /Subtype /Image /Width '+WIDTH+' /Height '+HEIGHT+' /ColorSpace /DeviceRGB /BitsPerComponent 8 /Filter /DCTDecode /Length '+jpeg.length+' >>\nstream\n'));
      append(jpeg);append(bytes('\nendstream\nendobj\n'));
      const drawing='q\n595.28 0 0 841.89 0 0 cm\n/Im0 Do\nQ\n';
      offsets[contentId]=position;
      append(bytes(contentId+' 0 obj\n<< /Length '+bytes(drawing).length+' >>\nstream\n'+drawing+'endstream\nendobj\n'));
    }
    const startXref=position, count=pages.length*3+3;
    append(bytes('xref\n0 '+count+'\n0000000000 65535 f \n'));
    for(let id=1;id<count;id++)append(bytes(String(offsets[id]).padStart(10,'0')+' 00000 n \n'));
    append(bytes('trailer\n<< /Size '+count+' /Root 1 0 R >>\nstartxref\n'+startXref+'\n%%EOF'));
    return new Blob(parts,{type:'application/pdf'});
  }

  function download(report) {
    if(!report || !Array.isArray(report.sections)||!report.sections.length)
      throw new Error('No report information available');
    const pages=reportPages(report);
    const blob=assemble(pages);
    const url=URL.createObjectURL(blob);
    const a=document.createElement('a');
    a.href=url;a.download=cleanFile(report.filename||'YanqhayCare_report');
    document.body.appendChild(a);a.click();a.remove();
    // Give the browser time to start downloading before revoking the object URL.
    setTimeout(()=>URL.revokeObjectURL(url),30000);
    return pages.length;
  }
  window.YanqhayPDF={download};
})();
