import React from 'react'

const HeaderComponent = () => {



  return (
    <div className=" bg-gradient-to-r from-slate-800 to-slate-900 shadow-md z-1 shadow-[rgba(0, 0, 0, 0.24) 0px 3px 8px] fixed w-[100%]">
      {/* Logo */}
      <div  className='m-auto flex items-center justify-between text-white w-[80%] py-4' >
          <a href='/'>
            <p className="text-lg font-semibold tracking-wide">
        AI <span className="text-blue-400">Product Analyzer</span>
      </p></a>

      {/* Menu */}
      <nav className="flex items-center gap-8 text-base font-medium">
        <a href="/detect" className="hover:text-blue-400 transition-colors duration-200">
          Phân tích
        </a>
        <a className="hover:text-blue-400 transition-colors duration-200 text-lg cursor-pointer">
          ?
        </a>
      </nav>
      </div>
    </div>

  );
}


export default HeaderComponent