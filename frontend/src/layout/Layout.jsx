import { Outlet } from 'react-router-dom'
import Footer from '../components/Footer.jsx'

const Layout = () => {
  return (
    <>         
      <Outlet/> 
      <Footer/>
    </>
  )
}

export default Layout
