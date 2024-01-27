<template>
  <div class="container mt-4">
    <form @submit.prevent="signup">
      <h3 align="center">Sign Up</h3>
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
        <label for="username">Username</label>
        <input
          type="text"
          id="username"
          name="username"
          class="form-control"
          placeholder="Enter Username"
          v-model="username"
        />
        <label for="password1">Password</label>
        <input
          type="password"
          id="password1"
          name="password1"
          class="form-control"
          placeholder="Enter Password"
          v-model='password1'
        />
        <label for="password2">Enter Password Again</label>
        <input
          type="password"
          id="password2"
          name="password2"
          class="form-control"
          placeholder="Enter Password Again"
          v-model="password2"
        />
        <br />
        <label for="image">Profile Image:</label>
        <input type="file" id="image" ref="image" @change="uploadImage"/>
        <br />
        <div align="center">
          <button class="btn btn-primary" type="submit">Sign Up</button>
        </div>
      </div>
    </form>
  </div>
</template>

<script>
import axios from 'axios'
export default {
    name: 'SignUp',
    data() {
    return { 
        email:'', 
        username:'',
        password1:'',
        password2:'',
        image:null
      }
    },
    methods: {
    async signup() {
      const formData = new FormData();
      formData.append("email", this.email);
      formData.append("username", this.username);
      formData.append("password1", this.password1);
      formData.append("password2", this.password2);
      formData.append("image", this.image);
      try {
        const response = await axios.post("/sign-up", formData,{
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
    },
    uploadImage(event) {
      this.image = event.target.files[0];
    }
  }
};
</script>