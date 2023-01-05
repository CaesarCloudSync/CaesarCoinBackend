'use strict'

const e = React.createElement;

class HelloWorld extends React.Component {
    constructor(props) {
        super(props);
        this.state = {brand: "Ford"};
      }
    remove = () => {
        this.setState({
          brand: "Bill"
        })
      }
    handleClick = () => {
        alert("Hello world")
    }

    render () {
        const {userid} = this.props;
        return <h1>Hello World <span onClick={this.remove}>{userid},{this.state.brand}</span></h1>
    }
}

// Find all DOM containers, and render our component into them.
var containers = document.querySelectorAll('.cfe-app')
containers.forEach(domContainer => {
    // Read the user ID from a data-* attribute.
    const userid = domContainer.dataset.userid
    // render the component into the DOM
    console.log(userid)
    ReactDOM.render(
      e(HelloWorld, { userid: userid}),
      domContainer
    )
});
