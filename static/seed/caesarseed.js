// ************************ Drag and drop ***************** //
const datetimeobj = new Date();
let dropArea = document.getElementById("drop-area")
companyname = "Google"
contributorname = "palondomus"
contributor_password = "kya63amari"
quotaname = "Googleman Text Classification"
blockchain_password = "kya63amari"
blockchain_name = "Caesar Block Chain"
window.onload= async function(){

  contributorsignup= await axios.post("http://127.0.0.1:5000/contributorsignin",json={"contributor":contributorname,"email":"amari.lawal05@gmail.com","password":contributor_password})

  if (contributorsignup.data.access_token == "Wrong password"){
    let walletbalance= document.getElementById("walletbalance")
    walletbalance.style = "margin-top:10px"
    walletbalance.innerHTML = `${contributorname} incorrect password or username.`
  }
  else{
    const config = {
      headers: { Authorization: `Bearer ${contributorsignup.data.access_token}` }
    };
    getlastblockchainresp = await axios.post("http://localhost:5000/get_wallet_balance",json={"blockchain_name":"Caesar Block Chain","blockchain_password":blockchain_password},config)  
    console.log(getlastblockchainresp.data.balance)
    const balance = getlastblockchainresp.data.balance
    let walletbalance= document.getElementById("walletbalance")
    walletbalance.style = "margin-top:10px"
    walletbalance.innerHTML = `${contributorname} wallet balance: ${balance} CN`
  }
  
  }

const client = new WebTorrent()
// Prevent default drag behaviors
;['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
  dropArea.addEventListener(eventName, preventDefaults, false)   
  document.body.addEventListener(eventName, preventDefaults, false)
})

// Highlight drop area when item is dragged over it
;['dragenter', 'dragover'].forEach(eventName => {
  dropArea.addEventListener(eventName, highlight, false)
})

;['dragleave', 'drop'].forEach(eventName => {
  dropArea.addEventListener(eventName, unhighlight, false)
})

// Handle dropped files
dropArea.addEventListener('drop', handleDrop, false)



function preventDefaults (e) {
  e.preventDefault()
  e.stopPropagation()
}

function highlight(e) {
  dropArea.classList.add('highlight')
}

function unhighlight(e) {
  dropArea.classList.remove('active')
}

function handleDrop(e) {
  
  var dt = e.dataTransfer
  //console.log(dt)
  var files = dt.files

  //console.log(files)
  handleFiles(files)
}

let uploadProgress = []
let progressBar = document.getElementById('progress-bar')

function initializeProgress(numFiles) {
  progressBar.value = 0
  uploadProgress = []

  for(let i = numFiles; i > 0; i--) {
    uploadProgress.push(0)
  }
}

function updateProgress(fileNumber, percent) {
  uploadProgress[fileNumber] = percent
  let total = uploadProgress.reduce((tot, curr) => tot + curr, 0) / uploadProgress.length
  progressBar.value = total
}

function createChunk(file,cSize) {
  let startPointer = 0;
  let counter = 0
  let endPointer = file.size;
  let chunks = [];
  while(startPointer<endPointer){
   let newStartPointer = startPointer+cSize;
   let fileSlice = file.slice(startPointer,newStartPointer)
   let fileSliceName = `${file.name}`
   var fileobj = new File([fileSlice], fileSliceName)
   chunks.push(fileobj);
   startPointer = newStartPointer;
   counter += 1;
  }
  return chunks;
 }

function handleFiles(files) {
  const file = [...files]
  //console.log(file[0].size)
  ////const 
  const chunksize =250_837_282.375  //200MB, 5_000 = 5KB 
  
  if (file[0].size > chunksize){
    const filechuncks = [createChunk(file[0],chunksize)]
    //console.log(filechuncks)
    filechuncks.forEach(caesartorrent)
  

  }
  else if (file[0].size < chunksize){
      initializeProgress(file.length)

      file.forEach(caesartorrent)
      if (file[0].name.includes(".png") || file[0].name.includes(".PNG") || file[0].name.includes(".jpg") || file[0].name.includes(".jpeg") || file[0].name.includes(".JPEG") || file[0].name.includes(".JPG") )
    {
      file.forEach(previewFile)
    }
  }


}

function previewFile(file) {
  let reader = new FileReader()
  reader.readAsDataURL(file)
  reader.onloadend = function() {
    let img = document.createElement('img')
    img.src = reader.result
    document.getElementById('gallery').appendChild(img)
  }
}
const hashBrowser = val =>
  crypto.subtle
    .digest('SHA-256', new TextEncoder('utf-8').encode(val))
    .then(h => {
      let hexes = [],
        view = new DataView(h);
      for (let i = 0; i < view.byteLength; i += 4)
        hexes.push(('00000000' + view.getUint32(i).toString(16)).slice(-8));
      return hexes.join('');
    });


async function caesartorrent(file, i) {
  let files = Array.isArray(file) ? file : [file]

  const signingresp = await axios.post('http://127.0.0.1:5000/contributorsignin',json={"contributor":contributorname,"email":"amari.lawal05@gmail.com","password":"kya63amari"})

  //console.log(signingresp.data.access_token)

const config = {
    headers: { Authorization: `Bearer ${signingresp.data.access_token}` }
};
const seedingresult = document.getElementById("seedingresult")
const loadingicon_container = document.createElement("div")
const loadingicon = document.createElement("div")
loadingicon.setAttribute("class", "loader");
loadingicon_container.setAttribute("class","loader_container")
loadingicon_container.setAttribute("id","loader_containerid")
loadingicon_container.appendChild(loadingicon)
seedingresult.appendChild(loadingicon_container)
// 1 nonce = 10 seconds overrall seeding
// 10 nonce = 1 seconds
var nonce_counter = 0
const initial_seeding_exchange = 10
const long_term_seeding_exchange = 0.02 // 0.01 will cause a coin to be awarded every 9 hours, 0,02 every 4 hours and 0.03, every 2 hours
const seed_nonce_reward_interval = 3*1000 //seconds
const mine_seed_reward_interval = Math.ceil((100/ long_term_seeding_exchange)*3)  *1000 
const nonce_to_coin_rate = 102.705882353
const coin_size_rate =500000000 //500MB
let start = Date.now();
// 349.2 nonce = 1.7GB = 34.99s
//205.411764706 nonce = 1GB
// 102.705882353 = 500MB = 1 coin = 0.01 up per 3 seconds
//  9.979 nonce = 48.5853100886MB =  1s
client.seed(files, async function(torrent){
  // TODO When Seeding large files it takes quite a while so use the time it takes to count the nonce as proof of work, then the general seeding will count to the extra nonce values for the block
    try{
      
      const initialValue = 0;
      const filesize = files.reduce(
        (accumulator, currentValue) => accumulator + currentValue.size,
        initialValue
      );
      const seedingresult = document.getElementById("seedingresult")
      const nonce_message_container = document.getElementById("nonce_counter");
      const seedmagneturi = document.getElementById("seedmagneturi")
      var progress_bar_container = document.createElement('div');
    
    
      progress_bar_container.setAttribute("class", "indeterminate-progress-bar");
      var progress_bar = document.createElement('div');
      progress_bar.setAttribute("class", "indeterminate-progress-bar__progress");
      progress_bar_container.appendChild(progress_bar)
    
      //console.log("Client seeding: " + torrent.magnetURI)
      var client_seeding_message = document.createElement('p')
      client_seeding_message.innerHTML = `Client seeding: ${files[0]["name"]}`
      
      var nonce_message = document.createElement('p')
      var nonce_count = document.createElement('p')

      
     
      seedmagneturi.style = "margin-left:400px;margin-right:400px"
    

      let coin_rewarded = Math.floor(filesize / coin_size_rate)

      
      
   
      const loader_containerid = document.getElementById("loader_containerid")
      loader_containerid.remove()
      seedmagneturi.appendChild(client_seeding_message)
      nonce_message.innerHTML = "nonce: "
      nonce_message_container.style = "display:flex;margin-left:400px;margin-right:400px"
      nonce_message_container.appendChild(nonce_message)
      nonce_message_container.appendChild(nonce_count)
      seedingresult.appendChild(progress_bar_container)
      // calculate the nonce 
      let end = Date.now();
      let initial_seeding_elapsed = (end-start)/1000
      let nonce_rewarded = Math.ceil(initial_seeding_elapsed * 10)
      nonce_counter += nonce_rewarded

      const storeresp = await axios.post('http://127.0.0.1:5000/storemagneturi',json={"companyname":companyname,"quotaname":quotaname,"torrentfilename":files[0]["name"],"contributorname":contributorname,"torrentmagneturi":torrent.magnetURI,"filesize":filesize},config)
      console.log(storeresp.data)

      if (storeresp.data.message !== "magneturi already exists"){
          const createblockresp= await axios.post("http://127.0.0.1:5000/create_blockchain",json={"blockchain_name":blockchain_name,"blockchain_privilege":"private","blockchain_password":blockchain_password},config)
          //console.log(createblockresp.data)
          const lastblockresp= await axios.post("http://127.0.0.1:5000/get_last_block",json={"blockchain_name":blockchain_name,"blockchain_password":blockchain_password},config)
          const lastblock = lastblockresp.data
          lastblock.transactions.push({"sender":"System","recipient":contributorname,"amount":coin_rewarded})

          const new_block  = {"index":lastblock.index +1,"transactions":lastblock.transactions,"timestamp":datetimeobj.getTime(),"previous_hash":lastblock.hash}
          const blockhash = await hashBrowser(JSON.stringify(new_block))
          new_block.hash = blockhash
          new_block.nonce = nonce_counter

          const newblockresp = await axios.post("http://127.0.0.1:5000/store_block",json={"blockchain_name":blockchain_name,"blockchain_password":blockchain_password,"block":new_block},config)
          //console.log(newblockresp.data)
      }
      async function createBlockchain(){
        const createblockresp= await axios.post("http://127.0.0.1:5000/create_blockchain",json={"blockchain_name":blockchain_name,"blockchain_privilege":"private","blockchain_password":blockchain_password},config)
        //console.log(createblockresp.data)
        const lastblockresp= await axios.post("http://127.0.0.1:5000/get_last_block",json={"blockchain_name":blockchain_name,"blockchain_password":blockchain_password},config)
        const lastblock = lastblockresp.data
        const seeding_coins_rewarded = Math.floor(nonce_counter / nonce_to_coin_rate) 
        lastblock.transactions.push({"sender":"System","recipient":contributorname,"amount":seeding_coins_rewarded})

        const new_block  = {"index":lastblock.index +1,"transactions":lastblock.transactions,"timestamp":datetimeobj.getTime(),"previous_hash":lastblock.hash}
        const blockhash = await hashBrowser(JSON.stringify(new_block))
        new_block.hash = blockhash
        new_block.nonce = nonce_counter

        const newblockresp = await axios.post("http://127.0.0.1:5000/store_block",json={"blockchain_name":blockchain_name,"blockchain_password":blockchain_password,"block":new_block},config)
        console.log(newblockresp.data)
      }
      window.setInterval(function(){
        // call your function here
        var nonce_buffer= nonce_counter + long_term_seeding_exchange 
        nonce_counter = Math.round(nonce_buffer * 100) / 100;
        nonce_count.innerHTML = nonce_counter
      }, seed_nonce_reward_interval);
      // This runs and generate coin every nine hours
      window.setInterval(function(){

        createBlockchain()
      }, mine_seed_reward_interval);

      window.addEventListener("beforeunload", (event) => {
        // When page is refreshed the block is stored
        if (nonce_counter > 100){
          createBlockchain()
        }
        
        //console.log("nonce value here: " + nonce_counter )

        event.preventDefault()
        });

  
    }
      
      catch(err){
        console.log(err)
      } 

  
    
  })

  









}
// New Function where after caesartorrent has been called 

/*  */