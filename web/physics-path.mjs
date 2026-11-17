import {normalizeState} from '../lib/protocol/session.mjs';
/** A display projection only. The complete session and its replay indices stay intact. */
export function physicsPath(session,{activeOnly=false}={}){
  const groups=[];
  for(const [index,state] of session.states.entries()){
    if(activeOnly&&index>session.cursor)break;
    const key=state.selector?normalizeState({...state,sourceInspection:undefined}).id:null;
    let group=groups.at(-1);
    if(!key||group?.key!==key){group={key,startIndex:index,endIndex:index,index,state,indices:[],current:false};groups.push(group);}
    group.indices.push(index);group.endIndex=index;
    if(!group.current){group.index=index;group.state=state;}
    if(index===session.cursor){group.current=true;group.index=index;group.state=state;}
  }
  return groups;
}

export function sourceInspectionHistory(session,describe=()=>null){
  return session.states.flatMap((state,index)=>{
    if(!state.sourceInspection)return [];
    const source=describe(state),label=source?.paperId?`${source.paperId} · ${source.endpointSide||'recorded'} method`:`Source inspection ${index+1}`;
    return [{index,label,active:index===session.cursor,target:state.sourceInspection}];
  });
}
