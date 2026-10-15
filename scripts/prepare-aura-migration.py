import json
import re
import sys
from pathlib import Path

root = Path(sys.argv[1])
app_path = root / 'src/App.tsx'
app = app_path.read_text()
if 'BrowserRouter' not in app or 'HashRouter' in app:
    raise SystemExit('Unexpected router configuration; inspect before migration')
routes = re.findall(r'<Route\s+path="([^"]+)"', app)
app = app.replace('BrowserRouter', 'HashRouter')
app = app.replace('<ServiceWorkerOptimizer />', '')
app = app.replace('<RoleBasedNavigation />', '<nav aria-label="209 Connect workspace" style={{padding:12,display:"flex",gap:16,flexWrap:"wrap"}}><a href="../products.html">Intentional Day</a><a href="../dashboard.html">Member profile</a><a href="../../index.html">209 website</a></nav><RoleBasedNavigation />')
app_path.write_text(app)

# Use the existing website sign-in outside hash routing. Both applications keep
# the same Supabase project and default session storage on the same origin.
auth_path = root / 'src/contexts/AuthContext.tsx'
auth_path.write_text('''import {createContext,useContext,useEffect,useState} from 'react';
import type {User,Session} from '@supabase/supabase-js';
import {supabase} from '@/integrations/supabase/client';
type AuthState={user:User|null;session:Session|null;loading:boolean;signInWithGoogle:()=>Promise<void>;signOut:()=>Promise<void>};
const AuthContext=createContext<AuthState|undefined>(undefined);
export function AuthProvider({children}:{children:React.ReactNode}){
 const [session,setSession]=useState<Session|null>(null);
 const [loading,setLoading]=useState(true);
 useEffect(()=>{let mounted=true,events=0;
 const {data:{subscription}}=supabase.auth.onAuthStateChange((_event,next)=>{events++;if(mounted){setSession(next);setLoading(false);}});
 const initialEvents=events;
 supabase.auth.getSession().then(({data,error})=>{if(mounted&&events===initialEvents){setSession(error?null:data.session);setLoading(false);}}).catch(()=>{if(mounted&&events===initialEvents)setLoading(false);});
 return()=>{mounted=false;subscription.unsubscribe();};},[]);
 async function signInWithGoogle(){window.location.assign('/david-sicairos-site/members/');}
 async function signOut(){const {error}=await supabase.auth.signOut();if(error)throw error;setSession(null);}
 return <AuthContext.Provider value={{user:session?.user??null,session,loading,signInWithGoogle,signOut}}>{children}</AuthContext.Provider>;
}
export function useAuth(){const value=useContext(AuthContext);if(!value)throw Error('Missing AuthProvider');return value;}
''')
index_path = root / 'index.html'
index = index_path.read_text()
index = re.sub(r'<title>.*?</title>', '<title>209 Connect — Product Workspace</title>', index, flags=re.S)
index_path.write_text(index)
(root / 'public/migration-routes.json').write_text(json.dumps({'status':'build-review-only','routes':routes,'mount':'/david-sicairos-site/members/aura/','data_migration':False},indent=2))
print(f'Prepared {len(routes)} route declarations for build review. Original repository unchanged.')
