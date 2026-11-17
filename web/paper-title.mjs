/** Small text-only display convenience, not a TeX renderer. Original titles remain data. */
export function paperTitle(value){
  const sub={'0':'₀','1':'₁','2':'₂','3':'₃','4':'₄','5':'₅','6':'₆','7':'₇','8':'₈','9':'₉','+':'₊','-':'₋'},sup={'0':'⁰','1':'¹','2':'²','3':'³','4':'⁴','5':'⁵','6':'⁶','7':'⁷','8':'⁸','9':'⁹','+':'⁺','-':'⁻'};
  return String(value??'').replace(/\$([^$\n]+)\$/g,(original,body)=>{
    if(!/^[A-Za-z0-9 ]*(?:[_^]\{[0-9+-]+\}[A-Za-z0-9 ]*)+$/.test(body))return original;
    return body.replace(/([_^])\{([0-9+-]+)\}/g,(_,mark,digits)=>[...digits].map(ch=>(mark==='_'?sub:sup)[ch]).join(''));
  });
}
