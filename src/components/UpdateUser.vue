<template>
    <form @submit.prevent="updateUser">
      <h3 align="center">Update Profile</h3>
      <div class="form-group">
        <label for="email">Email Address</label>
        <input type="email" id="email" name="email" class="form-control" v-model="email" />
        <br>
        <label for="username">Username</label>
        <input type="text" id="username" name="username" class="form-control" v-model="username" />
        <br />
        <div align="center">
            <button type="submit" class="btn btn-lg btn-primary">Update</button>
        </div>
        </div>
    </form>
    <br />
    <div align="center">
        <a v-bind:href="'/dashboard/' + username">
        <button type="button" class="btn btn-primary btn-lg">Back</button>
        </a>
    </div>
</template>

<script>
import axios from 'axios'
export default {
data() {
    return {
    email: "",
    username: "",
    }
},
methods: {
    async updateUser() {
      const formData = new FormData();
      formData.append("email", this.email);
      formData.append("username", this.username);
      try {
        const response = await axios.post("/update-user", formData,{
            headers: {
            Authorization: 'Bearer ' + localStorage.getItem('access_token')
        }
        });
        if (response.data.status === "success") {
            alert(response.data.message);
            this.$router.push(`/dashboard/${this.username}`);
        } else {
          alert(response.data.message);
        }
      } catch (error) {
        console.error(error);
        alert("An error occurred, please try again.");
      }
    }
  },
  mounted() {
    const headers = {
        Authorization: 'Bearer ' + localStorage.getItem('access_token'),
        };
    axios.get('/update-user', { headers })
    .then(response => {
      this.email = response.data.email;
      this.username= response.data.username;
    })
    .catch(error => {
        console.error(error);
    })
}
}
</script>