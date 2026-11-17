import copy,json,sys
from derive import old,separate_context
SCHEMA=copy.deepcopy(old.CHALLENGE_SCHEMA)
def evaluate(packet,reply):
 original=copy.deepcopy(reply);normalized,contexts=separate_context(reply);out=old.evaluate(packet,normalized);out.update(status='valid_derived_representation' if contexts else 'valid_original_representation',originalReplyValueSha256=old.base.vh(original),contextualDispositionReferences=contexts,originalScopeDispositions=original['scopeDispositions'],scientificContentChanged=False,discardedReferences=0);return out
if __name__=='__main__':
 if '--schema' in sys.argv:print(json.dumps(SCHEMA,indent=2));sys.exit()
 x=json.load(sys.stdin)
 try:print(json.dumps(evaluate(x['packet'],x['reply']),ensure_ascii=False,separators=(',',':')))
 except (AssertionError,KeyError,TypeError,ValueError) as e:print(json.dumps({'valid':False,'error':str(e)}));sys.exit(1)
