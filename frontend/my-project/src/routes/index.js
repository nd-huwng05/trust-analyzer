import { DetectPage } from "../page/DetectPage"
import { HomePage } from "../page/HomePage"


export const routes = [
    {
        path: "/",
        page: HomePage
    },
    {
        path: "/detect",
        page: DetectPage        
    }
]

export default routes