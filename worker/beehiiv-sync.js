// Private Beehiiv subscriber sync. Never writes public website files.
require('dotenv').config();
const {createClient}=require('@supabase/supabase-js');
async function sync(){
 for(const key of ['BEEHIIV_API_KEY','BEEHIIV_PUBLICATION_ID','SUPABASE_URL','SUPABASE_SERVICE_KEY'])if(!process.env[key])throw new Error('Missing configuration: '+key);
 const db=createClient(process.env.SUPABASE_URL,process.env.SUPABASE_SERVICE_KEY);
 const endpoint='https://api.beehiiv.com/v2/publications/'+process.env.BEEHIIV_PUBLICATION_ID+'/subscriptions';
 let cursor='',synced=0,pages=0;const seen=new Set();
 do{
  if(++pages>10000)throw new Error('Pagination limit reached; sync incomplete');
  const url=new URL(endpoint);url.searchParams.set('limit','100');if(cursor)url.searchParams.set('cursor',cursor);
  const res=await fetch(url,{headers:{Authorization:'Bearer '+process.env.BEEHIIV_API_KEY},signal:AbortSignal.timeout(60000)});
  if(!res.ok)throw new Error('Beehiiv request failed: HTTP '+res.status);
  const data=await res.json();if(!Array.isArray(data.data))throw new Error('Invalid subscription response');
  for(const s of data.data){
   if(typeof s.email!=='string'||!s.email)throw new Error('Subscription missing email; sync incomplete');
   const {error}=await db.from('audience_contacts').upsert({email:s.email,source:'beehiiv',engagement_status:s.status||'pending',beehiiv_data:{subscription_id:s.id,tier:s.subscription_tier||s.tier,tags:s.tags,stats:s.stats}},{onConflict:'email'});
   if(error)throw new Error('Supabase write failed; sync incomplete. Database code: '+(error.code||'unknown'));
   synced++;
  }
  cursor=data.next_cursor||'';
  if(data.has_more&&!cursor)throw new Error('Missing next cursor; sync incomplete');
  if(cursor&&seen.has(cursor))throw new Error('Repeated pagination cursor');
  if(cursor)seen.add(cursor);
 }while(cursor);
 console.log('Successfully wrote '+synced+' subscriber records across '+pages+' pages. No public files created.');
}
sync().catch(error=>{console.error(error.message);process.exitCode=1;});
