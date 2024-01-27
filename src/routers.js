import {createRouter, createWebHistory} from 'vue-router'
import HomePage from './components/HomePage'
import CreatePost from './components/CreatePost'
import LogIn from './components/LogIn'
import SignUp from './components/SignUp'
import PostDetail from './components/PostDetail'
import EditPost from './components/EditPost'
import DashBoard from './components/DashBoard'
import UpdatePassword from './components/UpdatePassword'
import UpdatePicture from './components/UpdatePicture'
import UpdateUser from './components/UpdateUser'
import FollowIng from './components/FollowIng'
import FollowErs from './components/FollowErs'
import ViewPosts from './components/ViewPosts'
import SearchUser from './components/SearchUser'
import SearchPost from './components/SearchPost'
import MyChart from './components/MyChart'
import CsvPost from './components/CsvPost'
import ResetPassword from './components/ResetPassword'

const routes = [
    {
        path:'/',
        name:'home',
        component:HomePage
    },
    {
        path:'/createpost',
        name:'createpost',
        component:CreatePost
    },
    {
        path:'/login',
        name:'login',
        component:LogIn,
        props:true
    },
    {
        path:'/signup',
        name:'signup',
        component:SignUp,
        props:true
    },
    {
        path:'/post/:id',
        name:'post',
        component:PostDetail,
        props:true
    },
    {
        path:'/edit/:id',
        name:'EditPost',
        component:EditPost,
        props:true
    },
    {
        path:'/dashboard/:username',
        name:'dashboard',
        component:DashBoard,
        props:true
    },
    {
        path:'/updatepassword',
        name:'updatepassword',
        component:UpdatePassword
    },
    {
        path:'/resetpassword',
        name:'resetpassword',
        component:ResetPassword
    },
    {
        path:'/updatepicture',
        name:'updatepicture',
        component:UpdatePicture
    },
    {
        path:'/updateuser',
        name:'updateuser',
        component:UpdateUser
    },
    {
        path:'/following/:username',
        name:'following',
        component:FollowIng,
        props:true
    },
    {
        path:'/followers/:username',
        name:'followers',
        component:FollowErs,
        props:true
    },
    {
        path:'/posts/:username',
        name:'posts',
        component:ViewPosts,
        props:true
    },
    {
        path: '/search-user',
        component: SearchUser,
        props: route => ({ username: route.query.name })
    },
    {
        path: '/search-post',
        component: SearchPost,
        props: route => ({ title: route.query.post_title })
      },
      {
          path:'/mychart',
          name:'mychart',
          component:MyChart
      },
      {
          path:'/csvpost',
          name:'csvpost',
          component:CsvPost
      }
]

const router = createRouter ({
    history:createWebHistory(),
    routes,
})

export default router;