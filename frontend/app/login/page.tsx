"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function LoginPage() {
  const router = useRouter();
  const [email,setEmail]=useState("");
  const [password,setPassword]=useState("");
  const [error,setError]=useState("");
  const [busy,setBusy]=useState(false);

  async function submit(e:FormEvent<HTMLFormElement>){
    e.preventDefault();setBusy(true);setError("");
    try{
      const response=await fetch(`${API}/api/v1/auth/login`,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({email,password})});
      const data=await response.json();
      if(!response.ok)throw new Error(data.detail||"Login failed");
      localStorage.setItem("dpm_erp_token",data.access_token);
      localStorage.setItem("dpm_erp_user",JSON.stringify(data.user));
      router.push("/");
    }catch(err){setError(err instanceof Error?err.message:"Unable to login");}
    finally{setBusy(false);}
  }

  return <main className="login"><form onSubmit={submit} className="login-card"><div className="brandmark">D</div><small>DPM ENTERPRISE · BUSINESS SUITE</small><h1>Welcome back</h1><p>Sign in to your company workspace.</p><label>Email address<input type="email" required autoComplete="username" value={email} onChange={e=>setEmail(e.target.value)}/></label><label>Password<input type="password" required autoComplete="current-password" value={password} onChange={e=>setPassword(e.target.value)}/></label>{error&&<div className="error">{error}</div>}<button disabled={busy}>{busy?"Signing in...":"Sign in securely"}</button><footer>Authorized DPM personnel only</footer></form><style jsx>{`
.login{min-height:100vh;background:#f4f6fa;display:grid;place-items:center;padding:20px;font-family:Arial,sans-serif;color:#1b2a42}.login-card{width:min(100%,410px);background:#fff;border:1px solid #e5eaf1;border-radius:14px;padding:36px;box-shadow:0 18px 55px #1b31530d}.brandmark{width:44px;height:44px;display:grid;place-items:center;background:#1b3153;color:white;border-radius:11px;font-size:25px;font-weight:bold;margin-bottom:20px}.login-card>small{font-size:9px;letter-spacing:1.5px;color:#8290a4}.login h1{font-size:25px;margin:12px 0 6px}.login p{font-size:12px;color:#8290a4;margin:0 0 25px}.login label{display:block;font-size:11px;font-weight:600;margin:15px 0}.login input{display:block;width:100%;height:42px;border:1px solid #dce3ec;border-radius:7px;margin-top:7px;padding:0 11px}.login button{width:100%;height:43px;background:#315fc6;color:white;border:0;border-radius:7px;font-weight:700;margin-top:8px}.login button:disabled{opacity:.6}.login footer{text-align:center;color:#9aa5b4;font-size:10px;margin-top:23px}.error{background:#fff0ef;color:#a13d36;padding:10px;border-radius:6px;font-size:11px}
`}</style></main>;
}
