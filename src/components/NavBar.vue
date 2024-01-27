<template>
  <div>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
      <div class="container-fluid">
        <button
          class="navbar-toggler"
          type="button"
          data-bs-toggle="collapse"
          data-bs-target="#navbar"
        >
          <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse" id="navbar">
          <div class="navbar-nav">
            <a v-if="!userloggedin" class="nav-item nav-link" href="/login">Login</a>
            <button
        class="btn btn-danger mX-3 mt-3" v-if="userloggedin" 
        @click="refresh">
        Refresh
        </button>
            <a v-if="!userloggedin" class="nav-item nav-link" href="/signup">SignUp</a>
            <a v-if="!userloggedin" class="nav-item nav-link" href="/resetpassword">Reset Password</a>
            <a v-if="userloggedin" class="nav-item nav-link" href="/">Home</a>
            <a v-if="userloggedin" class="nav-item nav-link" href="/createpost">Create Post</a>
            <a v-if="userloggedin" class="nav-item nav-link" @click="logout">Logout</a>
            <router-link
              :to="'/dashboard/' + username"
              class="nav-item nav-link" v-if="userloggedin" 
            >
              DashBoard
            </router-link>
            <router-link
              :to="'/posts/' + username"
              class="nav-item nav-link" v-if="userloggedin"
            >
              View Posts
            </router-link>
            <form v-if="userloggedin" action="/search-user" method="get" class="form-inline my-2 my-lg-0">
              <input
                class="form-control mr-sm-2"
                type="search"
                placeholder="Search User"
                aria-label="Search"
                name="name"
              />
              <button class="btn btn-outline-success my-2 my-sm-0" type="submit">
                Search
              </button>
            </form>
            <form v-if="userloggedin" action="/search-post" method="get" class="form-inline my-2 my-lg-0">
              <input
                class="form-control mr-sm-2"
                type="search"
                placeholder="Search post"
                aria-label="Search"
                name="post_title"
              />
              <button class="btn btn-outline-success my-2 my-sm-0" type="submit">
                Search
              </button>
            </form>
          </div>
        </div>
        <template v-if="url">
          <img :src="`http://127.0.0.1:5000${url}`" class="img-fluid rounded-circle small-image">
          <br />
        </template>
        <h5 style="color: white;">{{ username }}</h5>
      </div>
    </nav>
  </div>
</template>
<script>
import axios from 'axios'
export default {
  name: 'NavBar',
  data() {
    return {
    username:'',
    name:'',
    post:'',
    url:null
    }
  },
  methods: {
    logout() {
  axios.post('/logout', {}, {
      headers: {
          Authorization: 'Bearer ' + localStorage.getItem('access_token'),
          RefreshToken: 'Bearer ' + localStorage.getItem('refresh_token')
      }
  })
    .then(response => {
      if (response.data.status === 'success') {
        console.log(response.data.message);
        // remove access_token and refresh_token from local storage
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        this.userloggedin = false
        // redirect to the login page
        window.location.href = '/login';
      } else {
        console.log(response.data.status);
      }
    })
    .catch(error => {
      console.log(error);
    });
},
    async refresh() {
      try {
        const response = await axios.post('/refresh', {}, {
          headers: {
            Authorization: 'Bearer ' + localStorage.getItem('refresh_token')
          }
        })
        localStorage.setItem('access_token', response.data.access_token);
        location.reload();
      } catch (error) {
        console.error(error)
      }
    },
    getUser() {
  const headers = {
    Authorization: 'Bearer ' + localStorage.getItem('access_token'),
  };
  axios.get(`api/user`, { headers })
    .then(response => {
      this.username = response.data.username;
      this.url = response.data.url;
      this.userloggedin = true; // set a flag to show Home and Create Post links
    })
    .catch(error => {
      console.error(error);
    })
  }
  },
  mounted() {
    this.getUser()
  }
}
</script>

<style>
.rounded-circle {
  border-radius: 50%;
}

.small-image {
  width: 150px;
  height: 150px;
}
</style>