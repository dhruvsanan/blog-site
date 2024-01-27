<template>
    <form @submit.prevent="updateProfilePicture" enctype="multipart/form-data">
        <h1 align="center">Update your Profile Picture</h1>
        <div class="form-group">
        <br />
        <label for="image">Image:</label>
        <input type="file" id="image" ref="image" @change="uploadImage"/>
        <img :src="`http://127.0.0.1:5000${url}`" class="img-fluid">
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
    url: '',
    image:null,
    username:''
    }
},
methods: {
    async updateProfilePicture() {
      const formData = new FormData();
      formData.append("image", this.image);
      try {
        const response = await axios.post("/update-picture", formData,{
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
    },
    uploadImage(event) {
      this.image = event.target.files[0];
    }
  },
mounted() {
    const headers = {
        Authorization: 'Bearer ' + localStorage.getItem('access_token'),
        };
    axios.get('/update-picture', { headers })
    .then(response => {
        this.url = response.data.url;
        this.username= response.data.username;
    })
    .catch(error => {
        console.error(error);
    })
}
}
</script>
