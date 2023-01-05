const crEl = (tagName, attributes = {}, text) => {
  const el = document.createElement(tagName);
  Object.assign(el, attributes);
  if (text) { el.appendChild(document.createTextNode(text)); }

  return el;
};
/*
window.onload= async function(){
  companyname = "Google"
  company_password = "kya63amari"
  contributorsignup= await axios.post("http://127.0.0.1:5000/quotapostersignin",json={"company":companyname,"email":"amari.lawal05@gmail.com","password":company_password})
  
  if (contributorsignup.data.access_token == "Wrong password"){
    let walletbalance= document.getElementById("walletbalance")
    walletbalance.style = "position:absolute;left:20%;top:10%;"
    walletbalance.innerHTML = `${companyname} incorrect password or username.`
  }
  else{
    const config = {
      headers: { Authorization: `Bearer ${contributorsignup.data.access_token}` }
    };
    getlastblockchainresp = await axios.get("http://localhost:5000/getallmagneturi",config)  
    console.log(getlastblockchainresp.data.quotamagneturis)
    let someParentElement =  document.getElementById("quotamagneturiparent")
    //getlastblockchainresp.data.quotamagneturis.map(item => crEl("h1", {}, item.quotaname)).forEach(el => {someParentElement.appendChild(el)});
    //getlastblockchainresp.data.quotamagneturis.map(item => crEl("p", {}, item.torrentfilename)).forEach(el => {someParentElement.appendChild(el)});

  }
  
  }
*/
const client = new WebTorrent()
var blob_parts = []
const filenames = []
function downloadBlob(blob, name = 'file.txt') {
  // Convert your blob into a Blob URL (a special url that points to an object in the browser's memory)
  const blobUrl = URL.createObjectURL(blob);

  // Create a link element
  const link = document.createElement("a");

  // Set link's href to point to the Blob URL
  link.href = blobUrl;
  link.download = name;

  // Append link to the body
  document.body.appendChild(link);

  // Dispatch click event on the link
  // This is necessary as link.click() does not work on the latest firefox
  link.dispatchEvent(
    new MouseEvent('click', { 
      bubbles: true, 
      cancelable: true, 
      view: window 
    })
  );

  // Remove link from body
  document.body.removeChild(link);
}
function concatBlobs(blob, name = 'file.txt'){
    blob_parts.push(blob)


}
// Usage
//let jsonBlob = new Blob(['{"name": "test"}'])

client.on('error', function (err) {
  console.error('ERROR: ' + err.message)
})

document.querySelector('form').addEventListener('submit', async function (e) {
  e.preventDefault() // Prevent page refresh
  const quotapostingcontribution = document.querySelectorAll('.cfe-app')
  quotapostingcontribution.forEach(ele => ele.remove())
 
  
  const filename = document.querySelector('form input[name=torrentId]').value
  companyname = "Google"
  contributorname = "palondomus"
  quotaname = "Googleman Text Classification"
  //filename = "main.jpeg"
  const signingresp = await axios.post('http://127.0.0.1:5000/contributorsignin',json={"contributor":contributorname,"email":"amari.lawal05@gmail.com","password":"kya63amari"})
  //const torrentId = "https://webtorrent.io/torrents/sintel.torrent"
  const config = {
      headers: { Authorization: `Bearer ${signingresp.data.access_token}` }
  };
  const torrentmagneturi = await axios.post('http://127.0.0.1:5000/getmagneturi',json={"companyname":companyname,"quotaname":quotaname,"torrentfilename":filename},config)
  console.log(torrentmagneturi.data)
  const torrentId = torrentmagneturi.data.torrentmagneturi
  log('Adding ' + torrentId)
  client.add(torrentId, onTorrent)
})

function onTorrent (torrent) {

  log('Got torrent metadata!')
  log(
    'Torrent info hash: ' + torrent.infoHash + ' ' +
    '<a href="' + torrent.magnetURI + '" target="_blank">[Magnet URI]</a> ' +
    '<a href="' + torrent.torrentFileBlobURL + '" target="_blank" download="' + torrent.name + '.torrent">[Download .torrent]</a>'
  )
  const progresstext = document.createElement('p')
  progresstext.innerHTML = 'Progress: ' + (torrent.progress * 100).toFixed(1) + '%'
  document.querySelector(".log").appendChild(progresstext)
  // Print out progress every 5 seconds
  const interval = setInterval(function () {
    progresstext.innerHTML = 'Progress: ' + (torrent.progress * 100).toFixed(1) + '%'
  }, 5000)

  torrent.on('done', function () {
    log('Progress: 100%')
    clearInterval(interval)
  })

  // Render all files into to the page
  const initialValue = 0;
  const filesize = torrent.files.reduce(
  (accumulator, currentValue) => accumulator + currentValue.length,
  initialValue
);
  //console.log(filesize)
  filenames.push(torrent.files[0].name)
  torrent.files.forEach(async function (file) {
    const max_chunk_size = 200000000 /// 200MB, 5000 = 5KB
    const filename = document.querySelector('form input[name=torrentId]').value
    
   
    if (!file.name.includes("jpeg") && !file.name.includes("png")){
        if (filesize < max_chunk_size){

        file.getBlob(function callback (err, blob) {downloadBlob(blob, filename);})
        }
        else if (filesize > max_chunk_size){
          file.getBlob(function callback (err, blob) {concatBlobs(blob, blob.name)})

        }
    }
    else {
    file.appendTo('.log')
    log('(Blob URLs only work if the file is loaded from a server. "http//localhost" works. "file://" does not.)')
    file.getBlobURL(function (err, url) {
      if (err) return log(err.message)
      log('File done.')
      log('<a href="' + url + '">Download full file: ' + file.name + '</a>')
    })}
  })
  //console.log(torrentchunks)
}

function log (str) {
  const p = document.createElement('p')
  p.innerHTML = str
  document.querySelector('.log').appendChild(p)
}
var intvl = setInterval(function(){
  if (blob_parts.length !== 0){
    console.log(blob_parts)
  const new_blob = new Blob(blob_parts);
  console.log(filenames.slice(-1))
  if (filenames.length !== 0 || blob_parts.length !== 0){
   
  downloadBlob(new_blob,filenames.slice(-1))
}
  filenames.length = 0
  blob_parts.length = 0
  
  //clearInterval(intvl)
  }
  
},1000)