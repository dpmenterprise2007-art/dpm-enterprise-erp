"use client";

import { FormEvent, useEffect, useState } from "react";
import Link from "next/link";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

type Customer = { id: string; display_name: string; gstin: string | null; state_code: string | null };
type InvoiceResult = {
  id: string; invoice_number: string | null; status: string; grand_total: string;
  taxable_total: string; cgst_total: string; sgst_total: string; igst_total: string;
};

export default function NewInvoicePage() {
  const [customerId, setCustomerId] = useState("");
  const [customers, setCustomers] = useState<Customer[]>([]);
  const token = () => typeof window !== "undefined" ? localStorage.getItem("dpm_erp_token") || "" : "";
  const [invoiceDate, setInvoiceDate] = useState(new Date().toISOString().slice(0, 10));
  const [companyState, setCompanyState] = useState("27");
  const [supplyState, setSupplyState] = useState("27");
  const [description, setDescription] = useState("");
  const [hsn, setHsn] = useState("");
  const [quantity, setQuantity] = useState("1");
  const [rate, setRate] = useState("0");
  const [gst, setGst] = useState("18");
  const [result, setResult] = useState<InvoiceResult | null>(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  useEffect(() => { const t=token(); if(!t){ location.href="/login"; return; } fetch(`${API}/api/v1/customers`, {headers:{Authorization:`Bearer ${t}`}}).then(async r=>{if(r.status===401){location.href="/login";return;} if(r.ok){const d=await r.json();setCustomers(d);if(d[0]){setCustomerId(d[0].id);setSupplyState(d[0].state_code||"27");}}}).catch(()=>setError("Could not load customers")); }, []);

  async function createDraft(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); setBusy(true); setError(""); setResult(null);
    try {
      const response = await fetch(`${API}/api/v1/invoices`, {
        method: "POST", headers: { "Content-Type": "application/json", Authorization: `Bearer ${token()}` },
        body: JSON.stringify({
          customer_id: customerId,
          invoice_date: new Date(invoiceDate + "T12:00:00+05:30").toISOString(),
          place_of_supply: supplyState, company_state_code: companyState,
          lines: [{ description, hsn_sac: hsn || null, quantity, rate, gst_rate: gst, unit: "NOS" }]
        })
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || "Unable to create invoice draft");
      setResult(data);
    } catch (e) { setError(e instanceof Error ? e.message : "Request failed"); }
    finally { setBusy(false); }
  }

  async function issueInvoice() {
    if (!result) return;
    setBusy(true); setError("");
    try {
      const response = await fetch(`${API}/api/v1/invoices/${result.id}/issue`, { method: "POST", headers: { Authorization: `Bearer ${token()}` } });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || "Unable to issue invoice");
      setResult(data);
    } catch (e) { setError(e instanceof Error ? e.message : "Request failed"); }
    finally { setBusy(false); }
  }

  return <main className="invoice-page">
    <header><Link href="/">← Dashboard</Link><span>DPM ENTERPRISE ERP</span></header>
    <section className="invoice-wrap">
      <div className="heading"><div><small>SALES / INVOICES</small><h1>Create tax invoice</h1><p>Create a draft, verify tax details, then issue the invoice.</p></div><span className="draft-tag">GST BILLING</span></div>
      <form onSubmit={createDraft}>
        <div className="form-card"><h2>Customer & invoice details</h2>
          <label>Customer<select required value={customerId} onChange={e=>{setCustomerId(e.target.value);const selected=customers.find(c=>c.id===e.target.value);if(selected?.state_code)setSupplyState(selected.state_code);}}><option value="">Select customer</option>{customers.map(c=><option key={c.id} value={c.id}>{c.display_name}{c.gstin ? " · "+c.gstin : ""}</option>)}</select></label>{!customers.length && <p className="hint">Add a customer in Customer Master before creating an invoice.</p>}
          <div className="two"><label>Invoice date<input type="date" required value={invoiceDate} onChange={e=>setInvoiceDate(e.target.value)}/></label><label>Place of supply state code<input required maxLength={2} pattern="[0-9]{2}" value={supplyState} onChange={e=>setSupplyState(e.target.value)} placeholder="e.g. 27"/></label></div>
          <label>Company GST state code<input required maxLength={2} pattern="[0-9]{2}" value={companyState} onChange={e=>setCompanyState(e.target.value)} placeholder="Set from DPM GST registration"/></label>
        </div>
        <div className="form-card"><h2>Invoice item</h2>
          <label>Description<input required maxLength={240} value={description} onChange={e=>setDescription(e.target.value)} placeholder="Interior design / furniture / service description"/></label>
          <div className="three"><label>HSN / SAC<input maxLength={8} value={hsn} onChange={e=>setHsn(e.target.value)} placeholder="HSN/SAC"/></label><label>Quantity<input required type="number" min="0.001" step="0.001" value={quantity} onChange={e=>setQuantity(e.target.value)}/></label><label>Rate (₹)<input required type="number" min="0" step="0.01" value={rate} onChange={e=>setRate(e.target.value)}/></label></div>
          <label>GST rate (%)<select value={gst} onChange={e=>setGst(e.target.value)}><option value="0">0%</option><option value="5">5%</option><option value="12">12%</option><option value="18">18%</option><option value="28">28%</option></select></label>
        </div>
        <button className="submit" disabled={busy || !!result || !customers.length}>{busy ? "Processing..." : "Save invoice draft"}</button>
      </form>
      {error && <div className="error">{error}</div>}
      {result && <div className="result"><h2>{result.status === "issued" ? "Invoice issued" : "Draft saved"}</h2><p>Invoice ID: {result.id}</p><p>Number: {result.invoice_number || "Assigned when issued"}</p><p>Taxable: ₹{result.taxable_total} · CGST: ₹{result.cgst_total} · SGST: ₹{result.sgst_total} · IGST: ₹{result.igst_total}</p><strong>Grand total: ₹{result.grand_total}</strong>{result.status === "draft" ? <button className="submit" onClick={issueInvoice} disabled={busy}>{busy ? "Processing..." : "Issue invoice & assign number"}</button> : <a className="pdf" href={`${API}/api/v1/invoices/${result.id}/pdf`} target="_blank" rel="noreferrer">Open invoice PDF ↗</a>}</div>}
      <p className="warning">Development screen only. Confirm DPM GST registration state, customer place of supply, HSN/SAC and applicable tax rate before issuing. Accounting journal integration and statutory invoice configuration are still pending.</p>
    </section>
    <style jsx>{`
      .hint{font-size:11px;color:#987b3f}.invoice-page{min-height:100vh;background:#f5f7fb;color:#1a2940;font-family:Arial,sans-serif}header{height:65px;background:#fff;border-bottom:1px solid #e6ebf2;display:flex;align-items:center;justify-content:space-between;padding:0 5%;font-size:12px}header a{color:#315fc6;text-decoration:none}header span{font-weight:700;letter-spacing:1px}.invoice-wrap{max-width:850px;margin:38px auto;padding:0 20px}.heading{display:flex;justify-content:space-between;align-items:center;margin-bottom:24px}.heading small{font-size:10px;color:#8290a4;letter-spacing:1.3px}.heading h1{font-size:27px;margin:8px 0}.heading p{font-size:12px;color:#8491a4}.draft-tag{font-size:10px;font-weight:bold;color:#315fc6;background:#eaf0ff;padding:9px 12px;border-radius:6px}.form-card,.result{background:#fff;border:1px solid #e6ebf2;border-radius:10px;padding:22px;margin-bottom:16px}.form-card h2,.result h2{font-size:15px;margin:0 0 20px}.form-card label{display:block;font-size:11px;font-weight:600;color:#58677d;margin-bottom:15px}.form-card input,.form-card select{display:block;width:100%;height:40px;border:1px solid #dfe5ed;border-radius:6px;padding:0 10px;margin-top:7px;font:12px Arial;color:#253650;background:white}.two,.three{display:grid;grid-template-columns:repeat(2,1fr);gap:14px}.three{grid-template-columns:repeat(3,1fr)}.submit{border:0;background:#315fc6;color:white;padding:12px 18px;border-radius:7px;font-size:12px;font-weight:700;cursor:pointer}.submit:disabled{opacity:.55}.error{background:#fff0ef;color:#a23c35;padding:13px;border-radius:7px;font-size:12px;margin-top:15px}.result{margin-top:18px;font-size:12px;line-height:1.7}.result strong{display:block;margin:12px 0}.pdf{display:inline-block;color:#315fc6;font-weight:700;margin-top:10px}.warning{font-size:11px;line-height:1.6;color:#8a6a32;background:#fff8e9;padding:13px;border-radius:7px;margin-top:18px}@media(max-width:600px){.two,.three{grid-template-columns:1fr}.heading h1{font-size:22px}}
    `}</style>
  </main>;
}
