/** Fixed coordinates inside each recorded component; callouts move, anchors do not. */
export function classificationChartDisplay(nodes,{width,measureText=text=>text.length*7.2}={}){
  const mobile=width<900,margin=16,gap=8,fields=nodes.filter(node=>node.depth===0),band=mobile?0:Math.min(250,width*.23),plotX=mobile?margin:band+margin*2,plotWidth=mobile?width-margin*2:width-2*plotX;
  const wrap=(text,available)=>{const lines=[];let line='';for(const word of text.split(/\s+/)){const next=line?line+' '+word:word;if(line&&measureText(next)>available){lines.push(line);line=word;}else line=next;}if(line)lines.push(line);return lines;};
  const labelLines=new Map(fields.map(node=>[node.destinationId,wrap(node.title,band-28)])),cardHeight=mobile?0:Math.max(48,...[...labelLines.values()].map(lines=>lines.length*18+24)),height=mobile?450:Math.max(620,Math.ceil(fields.length/2)*(cardHeight+gap)+margin*2);
  const groups=new Map();for(const node of nodes){const key=node.component??0;if(!groups.has(key))groups.set(key,[]);groups.get(key).push(node);}
  const components=[...groups].sort((a,b)=>b[1].length-a[1].length),insetHeight=components.length>1?125:0,frames=[],points=[];
  for(let i=0;i<components.length;i++){
    const [component,group]=components[i],box=i===0?{x:plotX,y:margin,width:plotWidth,height:height-margin*2-insetHeight}:{x:plotX+(i-1)*plotWidth/(components.length-1),y:height-insetHeight,width:plotWidth/(components.length-1),height:insetHeight-margin};
    const xs=group.map(n=>n.x),ys=group.map(n=>n.y),minX=Math.min(...xs),maxX=Math.max(...xs),minY=Math.min(...ys),maxY=Math.max(...ys),padding=i?24:12,scale=Math.min((box.width-padding*2)/Math.max(.0001,maxX-minX),(box.height-padding*2)/Math.max(.0001,maxY-minY)),cx=(minX+maxX)/2,cy=(minY+maxY)/2;
    for(const node of group)points.push({...node,x:box.x+box.width/2+(node.x-cx)*scale,y:box.y+box.height/2+(node.y-cy)*scale});
    if(i)frames.push({...box,component,label:'Separate classification component',transform:{scale,sourceCenter:[cx,cy]}});
  }
  const byId=new Map(points.map(point=>[point.destinationId,point])),callouts=[];
  if(!mobile){
    const sorted=[...fields].sort((a,b)=>byId.get(a.destinationId).x-byId.get(b.destinationId).x||a.destinationId.localeCompare(b.destinationId)),halves=[sorted.slice(0,Math.ceil(sorted.length/2)),sorted.slice(Math.ceil(sorted.length/2))];
    halves.forEach((half,side)=>{half.sort((a,b)=>byId.get(a.destinationId).y-byId.get(b.destinationId).y||a.destinationId.localeCompare(b.destinationId));half.forEach((node,i)=>{const anchor=byId.get(node.destinationId),y=margin+i*(cardHeight+gap);callouts.push({destinationId:node.destinationId,x:side?width-margin-band:margin,y,width:band,height:cardHeight,lines:labelLines.get(node.destinationId),anchor,side});});});
  }
  return{width,height,mobile,points,callouts,frames};
}
