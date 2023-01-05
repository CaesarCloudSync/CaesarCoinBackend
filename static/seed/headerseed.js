'use strict'

const headerelement = React.createElement;
/*
$("#search-icon").click(function() {
  $(".nav").toggleClass("search");
  $(".nav").toggleClass("no-search");
  $(".search-input").toggleClass("search-active");
});

$('.menu-toggle').click(function(){
   $(".nav").toggleClass("mobile-nav");
   $(this).toggleClass("is-active");
}); */
class HelloWorld extends React.Component {
    constructor(props) {
        super(props);
        this.state = {moblenaved: 0};
        //this.handleClick = this.handleClick.bind(this);
      }
    remove = () => {

      }
    handleClick = () => {
      console.log()
      if (this.state.moblenaved == 0){
        this.setState({
          moblenaved: 1
        })

      }
      else if (this.state.moblenaved == 1){
        this.setState({
          moblenaved: 0
        })
      }

    }

    render () {

        return (
        <div>


<div class="page-wrapper">
 <div class="nav-wrapper">
  <div class="grad-bar"></div>
  <nav class="navbar">
    <img src="https://revisionbank.org/static/media/RevisionBankLogo.ecc9930c0b9300dfc7d423d26560046d.svg" alt="Company Logo"></img>
    <div class="menu-toggle" id="mobile-menu" onClick={this.handleClick}>
      <span class="bar"></span>
      <span class="bar"></span>
      <span class="bar"></span>
    </div>
    { this.state.moblenaved === 0 ? 
        <ul class="nav no-search">
        <li class="nav-item"><a href="#">Home</a></li>
        <li class="nav-item"><a href="#">About</a></li>
        <li class="nav-item"><a href="#">Work</a></li>
        <li class="nav-item"><a href="#">Careers</a></li>
        <li class="nav-item"><a href="#">Contact Us</a></li>
        <i class="fas fa-search" id="search-icon" ></i>
        <input class="search-input" type="text" placeholder="Search.."></input>
      </ul>:
      <ul class="mobile-nav no-search">
        <li class="nav-item"><a href="#">Home</a></li>
        <li class="nav-item"><a href="#">About</a></li>
        <li class="nav-item"><a href="#">Work</a></li>
        <li class="nav-item"><a href="#">Careers</a></li>
        <li class="nav-item"><a href="#">Contact Us</a></li>
        <i class="fas fa-search" id="search-icon" ></i>
        <input class="search-input" type="text" placeholder="Search.."></input>
      </ul>
        }

  </nav>
  </div>
</div>



        </div>)
    }
}

// Find all DOM containers, and render our component into them.
var containers = document.querySelectorAll('.headersection')
containers.forEach(domContainer => {

    ReactDOM.render(
      headerelement(HelloWorld),
      domContainer
    )
});
