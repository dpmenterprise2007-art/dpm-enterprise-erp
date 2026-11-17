import { ArrowUpRight, Bell, BriefcaseBusiness, CalendarDays, FileText, LayoutDashboard, Package, Plus, Search, Settings, ShoppingCart, Users, Wallet, ChartNoAxesCombined, ReceiptText } from "lucide-react";

const links = [
  ["Overview", LayoutDashboard], ["Sales & Invoices", FileText], ["Purchase", ShoppingCart],
  ["Parties", Users], ["Items & Inventory", Package], ["Accounting", Wallet],
  ["Expenses", ReceiptText], ["Projects", BriefcaseBusiness], ["Reports", ChartNoAxesCombined],
] as const;

const stats = [
  ["Total sales", "₹0.00", "No transactions recorded"],
  ["Receivables", "₹0.00", "Customer outstanding"],
  ["Total purchase", "₹0.00", "No bills recorded"],
  ["Cash & bank", "₹0.00", "Opening balances pending"],
];

export default function Home() {
  return <main className="shell">
    <aside className="sidebar">
      <div className="brand"><div className="mark">D</div><div><b>DPM <span>ENTERPRISE</span></b><small>BUSINESS SUITE</small></div></div>
      <div className="label">WORKSPACE</div><div className="company">▦ <span>DPM Enterprise Pvt. Ltd.</span>⌄</div>
      <div className="label menu-label">MENU</div>
      <nav>{links.map(([name, Icon], i) => <a className={i===0?"nav active":"nav"} href="#" key={name}><Icon size={18}/>{name}</a>)}</nav>
      <div className="side-bottom"><a className="nav" href="#"><Settings size={18}/>Settings</a><div className="user"><div className="avatar">DP</div><div><b>DPM Administrator</b><small>Administrator</small></div></div></div>
    </aside>
    <section className="main">
      <header className="top"><div className="crumb">Workspace <span>/</span> <b>Overview</b></div><div className="tools"><div className="search"><Search size={16}/> Search anything...</div><Bell size={18}/><div className="avatar">DP</div></div></header>
      <div className="content">
        <div className="welcome"><div><small className="eyebrow">DPM ENTERPRISE · BUSINESS OVERVIEW</small><h1>Good evening</h1><p>Here’s what’s happening with your business.</p></div><button className="primary"><Plus size={17}/> Create new</button></div>
        <div className="notice"><b>Workspace setup</b><span>Configure company details, opening balances and your first customer to get started.</span></div>
        <div className="section"><div><h2>Business overview</h2><p>Financial snapshot for your company.</p></div><button className="filter"><CalendarDays size={15}/> This financial year</button></div>
        <div className="stats">{stats.map(([name,value,note],i)=><article className="card" key={name}><div className="stat-head"><span>{name}</span><span className={`dot d${i}`}></span></div><strong>{value}</strong><small>{note}</small></article>)}</div>
        <div className="panels"><article className="panel"><div><h3>Sales performance</h3><p>Revenue overview for the selected period</p></div><div className="empty"><ChartNoAxesCombined size={27}/><b>No sales data yet</b><span>Your sales trend will appear here after invoices are recorded.</span></div></article><article className="panel"><div><h3>Quick actions</h3><p>Common tasks, one click away</p></div><div className="actions">{[["Create invoice","Bill a customer"],["Add customer","Create a party account"],["Add an item","Products and services"],["Record expense","Track business spending"]].map(([a,b])=><button key={a}><span><b>{a}</b><small>{b}</small></span><ArrowUpRight size={16}/></button>)}</div></article></div>
        <footer>© DPM ENTERPRISE PRIVATE LIMITED <span>ERP V1.0 · Foundation preview</span></footer>
      </div>
    </section>
  </main>;
}
