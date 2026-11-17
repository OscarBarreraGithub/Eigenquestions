/** Display-only packing of classification labels. Stored coordinates and edges are unchanged. */
export function classificationDisplayLayout(nodes,{width,measureText=text=>text.length*7.2}={}) {
  const margin=14,gap=12,columns=Math.max(1,Math.min(nodes.length,Math.floor((width-2*margin+gap)/(width<520?158:210)))),rows=Math.ceil(nodes.length/columns),cardWidth=(width-2*margin-gap*(columns-1))/columns;
  const wrap=text=>{const lines=[];let line='';for(const word of text.split(/\s+/)){const next=line?line+' '+word:word;if(line&&measureText(next)>cardWidth-28){lines.push(line);line=word;}else line=next;}if(line)lines.push(line);return lines;};
  const labels=nodes.map(node=>wrap(node.title)),cardHeight=Math.max(52,...labels.map(lines=>lines.length*18+24)),height=2*margin+rows*cardHeight+(rows-1)*gap;
  if(!nodes.length)return{width,height:0,nodes:[]};
  const xs=nodes.map(n=>n.x),ys=nodes.map(n=>n.y),x0=Math.min(...xs),y0=Math.min(...ys),dx=Math.max(...xs)-x0||1,dy=Math.max(...ys)-y0||1;
  const slots=Array.from({length:rows*columns},(_,i)=>({x:margin+(i%columns)*(cardWidth+gap)+cardWidth/2,y:margin+Math.floor(i/columns)*(cardHeight+gap)+cardHeight/2}));
  const target=nodes.map(n=>({x:margin+cardWidth/2+(n.x-x0)/dx*Math.max(0,width-2*margin-cardWidth),y:margin+cardHeight/2+(n.y-y0)/dy*Math.max(0,height-2*margin-cardHeight)}));
  // Rectangular Hungarian assignment: minimize displacement to distinct label-sized slots.
  const n=nodes.length,m=slots.length,u=Array(n+1).fill(0),v=Array(m+1).fill(0),p=Array(m+1).fill(0),way=Array(m+1).fill(0);
  for(let i=1;i<=n;i++){
    p[0]=i;let j0=0;const minv=Array(m+1).fill(Infinity),used=Array(m+1).fill(false);
    do{used[j0]=true;const i0=p[j0];let delta=Infinity,j1=0;
      for(let j=1;j<=m;j++)if(!used[j]){const cost=(target[i0-1].x-slots[j-1].x)**2+(target[i0-1].y-slots[j-1].y)**2-u[i0]-v[j];if(cost<minv[j]){minv[j]=cost;way[j]=j0;}if(minv[j]<delta){delta=minv[j];j1=j;}}
      for(let j=0;j<=m;j++)if(used[j]){u[p[j]]+=delta;v[j]-=delta;}else minv[j]-=delta;
      j0=j1;
    }while(p[j0]);
    do{const j1=way[j0];p[j0]=p[j1];j0=j1;}while(j0);
  }
  const assignment=Array(n);for(let j=1;j<=m;j++)if(p[j])assignment[p[j]-1]=slots[j-1];
  return{width,height,nodes:nodes.map((node,i)=>({...node,...assignment[i],width:cardWidth,height:cardHeight,lines:labels[i]}))};
}
