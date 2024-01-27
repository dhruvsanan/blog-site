<template>
    <div class="container mt-4">
    <form @submit.prevent="login">
      <h3 align="center">Login</h3>
      <div class="form-group">
        <label for="email">Email Address</label>
        <input
          type="email"
          id="email"
          name="email"
          class="form-control"
          placeholder="Enter Email"
          v-model='email'
        />
        <label for="password">Password</label>
        <input
          type="password"
          id="password"
          name="password"
          class="form-control"
          placeholder="Enter Password"
          v-model='password'
        />
        <br />
        <div align="center">
          <button class="btn btn-primary" type="submit">Login</button>
        </div>
      </div>
    </form>
    </div>
</template>

<script>
import axios from 'axios'
export default {
    name: 'LogIn',
    data() {
    return { 
        email:'', 
        password:''
    }
    },
    methods: {
      async login() {
        const formData = new FormData();
        formData.append("email", this.email);
        formData.append("password", this.password);
        try {
          const response = await axios.post('/login', formData,{
          headers: {
            "Content-Type": "multipart/form-data"
          }
        });
        localStorage.setItem('access_token', response.data.access_token);
        localStorage.setItem('refresh_token', response.data.refresh_token);
            if (response.data.status === "success") {
              alert(response.data.message);
              this.$router.push("/");
              setTimeout(() => {
                window.location.reload();
              }, 0);
            } else {
              alert(response.data.message);
            }
          } catch (error) {
            console.error(error);
            alert("An error occurred, please try again.");
          }
        }
      }
}
</script>