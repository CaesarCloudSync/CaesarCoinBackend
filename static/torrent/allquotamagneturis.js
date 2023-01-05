'use strict'
const e = React.createElement;
class Comp1 extends React.Component {
    constructor(props) {
       super(props);
       this.getallmagneuris = this.getallmagneuris.bind(this);
       this.state = {quotas:[]}
    }
   
    componentDidMount() {
       //window.addEventListener('load', this.handleLoad);
       this.getallmagneuris();
       //alert("Hi")
    }
    async getallmagneuris(){
        const companyname = "Google"
        const company_password = "kya63amari"
        const contributorsignup= await axios.post("http://127.0.0.1:5000/quotapostersignin",{"company":companyname,"email":"amari.lawal05@gmail.com","password":company_password})
        
        //console.log(contributorsignup)
        if (contributorsignup.data.access_token == "Wrong password"){
          let walletbalance= document.getElementById("walletbalance")
          walletbalance.style = "position:absolute;left:20%;top:10%;"
          walletbalance.innerHTML = `${companyname} incorrect password or username.`
        }
        else{
          const config = {
            headers: { Authorization: `Bearer ${contributorsignup.data.access_token}` }
          };
          const getlastblockchainresp = await axios.get("http://localhost:5000/getallmagneturi",config) 
          //console.log(getlastblockchainresp.data.quotamagneturis)
          this.setState( state => ({
            quotas: state.quotas.concat(getlastblockchainresp.data.quotamagneturis)
        }));
  
        }
    }
    render () {
        //console.log(this.state)
        const quotas = this.state.quotas
        return (
          <div>
            <h1>Quota files Contributed</h1>
            {
              quotas.length > 0 &&
                <div>
                  {quotas.map((quota,idx) => {return (
                    <div>
                      <p>Quota {idx+1}: {quota.quotaname}</p>
                      <p style={{color:"white"}}>Contributed Filename: {quota.torrentfilename}</p>
                      <br></br>
                      
                    </div>
                  )})}
                </div>
            }

          </div>
        )
    }
}


// Find all DOM containers, and render our component into them.
var containers = document.querySelectorAll('.cfe-app')
containers.forEach(domContainer => {
    // Read the user ID from a data-* attribute.
    const userid = domContainer.dataset.userid
    // render the component into the DOM
    ReactDOM.render(
      e(Comp1, { userid: userid}),
      domContainer
    )
});