/* ── TYPED JS ── */
new Typed('#typed-el', {
  strings:[
    'AI Engineer',
    'Data Scientist',
    'Agentic AI Developer',
    'RAG Systems Architect',
    'MLOps Engineer',
    'Kaggle Grandmaster 🏆',
  ],
  typeSpeed:55,backSpeed:32,backDelay:2000,
  loop:true,cursorChar:'|',smartBackspace:true
});

/* ── MOBILE NAV ── */
const ham=document.getElementById('ham');
const navMenu=document.getElementById('navMenu');
ham.addEventListener('click',()=>navMenu.classList.toggle('open'));
navMenu.querySelectorAll('a').forEach(a=>a.addEventListener('click',()=>navMenu.classList.remove('open')));

/* ── ACTIVE NAV HIGHLIGHT ── */
const secs=document.querySelectorAll('section[id]');
const navAs=document.querySelectorAll('.nav-menu a');
window.addEventListener('scroll',()=>{
  let cur='';
  secs.forEach(s=>{if(window.scrollY>=s.offsetTop-200)cur=s.id});
  navAs.forEach(a=>{
    a.classList.toggle('active',a.getAttribute('href')==='#'+cur);
  });
},{ passive:true });

/* ── SCROLL REVEAL ── */
const revEls=document.querySelectorAll('.reveal');
const io=new IntersectionObserver(entries=>{
  entries.forEach(e=>{if(e.isIntersecting){e.target.classList.add('vis');io.unobserve(e.target)}});
},{threshold:.08,rootMargin:'0px 0px -50px 0px'});
revEls.forEach(el=>io.observe(el));

/* ── RESUME DOWNLOAD ── */
function downloadResume(){
  // Replace with your hosted PDF URL
  const url='YOUR_RESUME_PDF_URL_HERE';
  const a=document.createElement('a');
  a.href=url;a.download='Asadullah_Shehbaz_Resume.pdf';a.target='_blank';
  document.body.appendChild(a);a.click();document.body.removeChild(a);
}
document.getElementById('resumeBtn')?.addEventListener('click',downloadResume);

/* ── CHATBOT ── */
// Replace this with your FastAPI endpoint when ready
const API_ENDPOINT = 'http://localhost:8000/chat';
  
const chatFab=document.getElementById('chatFab');
const chatPanel=document.getElementById('chatPanel');
const cpClose=document.getElementById('cpClose');
const cpMsgs=document.getElementById('cpMsgs');
const cpInput=document.getElementById('cpInput');
const cpSend=document.getElementById('cpSend');
const cpQuick=document.getElementById('cpQuick');

let isOpen=false;

function toggleChat(state){
  isOpen = state !== undefined ? state : !isOpen;
  chatPanel.classList.toggle('open',isOpen);
  chatFab.classList.toggle('open',isOpen);
  chatFab.querySelector('.ic-chat').style.display = isOpen ? 'none' : 'block';
  chatFab.querySelector('.ic-close').style.display = isOpen ? 'block' : 'none';
  if(isOpen) cpInput.focus();
}

chatFab.addEventListener('click',()=>toggleChat());
cpClose.addEventListener('click',()=>toggleChat(false));

function nowTime(){
  return new Date().toLocaleTimeString([],{hour:'2-digit',minute:'2-digit'});
}

function addMsg(text,role){
  const div=document.createElement('div');
  div.className=`cm cm-${role}`;
  div.innerHTML=`<div class="cm-bubble">${text}</div><div class="cm-time">${nowTime()}</div>`;
  div.style.animationDelay='0s';
  cpMsgs.appendChild(div);
  cpMsgs.scrollTop=cpMsgs.scrollHeight;
}

function showTyping(){
  const d=document.createElement('div');
  d.className='cm typing-row';d.id='typingEl';
  d.innerHTML=`<div class="typing-bub"><span></span><span></span><span></span></div>`;
  cpMsgs.appendChild(d);
  cpMsgs.scrollTop=cpMsgs.scrollHeight;
}
function hideTyping(){document.getElementById('typingEl')?.remove()}

// const demoReplies=[
//   "I specialize in Agentic AI pipelines, RAG architectures, LangGraph, FastAPI, MLOps, and n8n automation. I've built 11+ production AI systems. What specifically interests you?",
//   "I've built projects across agentic AI, RAG, computer vision, NLP, and ML automation. My latest is an AI Voice Receptionist for dental clinics. Check the Projects section for live demos!",
//   "Yes! I'm available for freelance and remote work. I can build AI agents, RAG systems, automation workflows, or end-to-end ML pipelines. Reach me at asadullahcreative@gmail.com.",
//   "I'm ranked #26 globally on Kaggle in Datasets — achieved both Grandmaster and Notebook Expert tiers in just 11 months. You can view my Kaggle profile for details.",
//   "My tech stack includes Python, LangChain, LangGraph, FastAPI, Docker, MLflow, FAISS, ChromaDB, n8n, ElevenLabs, Groq API, TensorFlow, PyTorch, and more.",
//   "I completed internships at Elevo Pathways (ML Engineer) and Skilled Score (Data Science) in 2025, where I built and deployed ML solutions for real business problems.",
// ];

async function sendMsg(text){
  if(!text.trim())return;
  cpQuick.style.display='none';
  cpInput.value='';
  cpSend.disabled=true;
  addMsg(text,'user');
  showTyping();

  /* ── Uncomment below & remove demo section to use your real FastAPI ──*/
  try{
    const res=await fetch(API_ENDPOINT,{
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body:JSON.stringify({message:text})
    });
    const data=await res.json();
    hideTyping();
    addMsg(data.response||data.answer||data.message,'bot');
  }catch(err){
    hideTyping();
    addMsg('⚠️ Unable to connect to the API. Check your endpoint configuration.','bot');
  }
  /*── end real API section ── */

  // DEMO MODE — remove when connecting real API_ENDPOINT
  // setTimeout(()=>{
  //   hideTyping();
  //   addMsg(demoReplies[Math.floor(Math.random()*demoReplies.length)],'bot');
  //   cpSend.disabled=false;
  // },1200+Math.random()*700);
}

cpSend.addEventListener('click',()=>sendMsg(cpInput.value));
cpInput.addEventListener('keydown',e=>{
  if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();sendMsg(cpInput.value)}
});

function quickSend(t){sendMsg(t)}
