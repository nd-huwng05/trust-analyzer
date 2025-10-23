import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import './App.css'
import routes from './routes'
import HeaderComponent from './components/HeaderComponent'
import FooterComponent from './components/FooterComponent'

function App() {
  return (
      <div className='h-full'>
        <HeaderComponent />
        <Router>
          <Routes>
            {
              routes.map((route, index) => (
                <Route
                  key={index}
                  path={route.path}
                  element={<route.page />}
                />
              ))
            }
          </Routes>
        </Router>
        <FooterComponent />
      </div>

  )
}

export default App
