<template>
    <div>
      <form @submit.prevent="updatePassword">
        <h3 align="center">Update Profile</h3>
        <div class="form-group">
          <label for="password1">Password</label>
          <input
            type="password"
            id="password1"
            name="password1"
            v-model="password1"
            class="form-control"
            placeholder="Enter Password"
          />
          <label for="password2">Password Again</label>
          <input
            type="password"
            id="password2"
            name="password2"
            v-model="password2"
            class="form-control"
            placeholder="Enter Password Again"
          />
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
</div>
</template>

<script>
import axios from 'axios'
export default {
data() {
    return {
    password1: '',
      password2: '',
      username:''
    }
},
methods: {
    async updatePassword() {
      const formData = new FormData();
      formData.append("password1", this.password1);
      formData.append("password2", this.password2);
      try {
        const response = await axios.post("/update-password", formData,{
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
    axios.get('/update-password', { headers })
    .then(response => {
        this.username= response.data.username;
    })
    .catch(error => {
        console.error(error);
    })
}
};
</script>
