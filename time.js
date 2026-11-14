/* IANA time zones, evaluated for the selected instant by the device's Intl database. */
(function(root){
const cache=new Map();
function parts(ms,zone){let f=cache.get(zone);if(!f){f=new Intl.DateTimeFormat('en-CA',{timeZone:zone,year:'numeric',month:'2-digit',day:'2-digit',hour:'2-digit',minute:'2-digit',second:'2-digit',hourCycle:'h23'});cache.set(zone,f)}return Object.fromEntries(f.formatToParts(new Date(ms)).filter(p=>p.type!=='literal').map(p=>[p.type,p.value]));}
function fields(ms,z){const p=parts(ms,z);return {date:`${p.year}-${p.month}-${p.day}`,time:`${p.hour}:${p.minute}`};}
function offset(ms,z){const p=parts(ms,z);return (Date.UTC(+p.year,+p.month-1,+p.day,+p.hour,+p.minute,+p.second)-Math.floor(ms/1000)*1000)/60000;}
function candidates(date,time,z){if(!/^\d{4}-\d{2}-\d{2}$/.test(date)||!/^\d{2}:\d{2}$/.test(time))return [];const [y,m,d]=date.split('-').map(Number),[h,n]=time.split(':').map(Number);if(y<1900||y>2100||h>23||n>59)return [];const utc=Date.UTC(y,m-1,d,h,n);if(new Date(utc).toISOString().slice(0,10)!==date)return [];const offsets=new Set();for(let i=-48;i<=48;i+=3)offsets.add(offset(utc+i*3600000,z));return [...offsets].map(o=>utc-o*60000).filter(t=>{const p=fields(t,z);return p.date===date&&p.time===time}).sort((a,b)=>a-b);}
function gmt(ms,z){const o=offset(ms,z);return 'UTC'+(o<0?'−':'+')+String(Math.floor(Math.abs(o)/60)).padStart(2,'0')+':'+String(Math.abs(o)%60).padStart(2,'0');}
root.TimeClub={parts,fields,offset,candidates,gmt};
})(typeof module==='object'?module.exports:globalThis);
