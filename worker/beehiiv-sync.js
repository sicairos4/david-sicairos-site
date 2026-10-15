// Beehiiv → Supabase audience sync
// Env: BEEHIIV_API_KEY, BEEHIIV_PUBLICATION_ID, SUPABASE_URL, SUPABASE_SERVICE_KEY
require('dotenv').config();
const { createClient } = require('@supabase/supabase-js');
const supabase = createClient(process.env.SUPABASE_URL, process.env.SUPABASE_SERVICE_KEY);
const BEEHIIV='https://api.beehiiv.com/v2/publications/'+process.env.BEEHIIV_PUBLICATION_ID+'/subscriptions';
async function sync(){
let cursor='';let synced=0;
do{
const res=await fetch(BEEHIIV+'?limit=100'+(cursor?'&cursor='+cursor:''),{headers:{Authorization:'Bearer '+process.env.BEEHIIV_API_KEY}});
const data=await res.json();
const subs=data.data||[];
for(const s of subs){
const{error}=await supabase.from('audience_contacts').upsert({
email:s.email,source:'beehiiv',engagement_status:s.status||'pending',
beehiiv_data:{subscription_id:s.id,tier:s.tier,tags:s.tags,stats:s.stats}
},{onConflict:'email'});
if(!error)synced++;
}
cursor=data.pagination&&data.pagination.next_cursor?data.pagination.next_cursor:'';
}while(cursor);
console.log('Synced '+synced+' Beehiiv subscribers');
}
sync();