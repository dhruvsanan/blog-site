<template>
  <div class="container mt-4">
    <h1 align="center">Make a Post</h1>
    <form @submit.prevent="create_post">
      <div class="form-group">
        <label for="title">Title</label>
        <input
          type="text"
          id="title"
          name="title"
          class="form-control"
          placeholder="Title"
          v-model='title'
        />
        <br>
        <label for="text">Caption/Description</label>
        <textarea
          type="text"
          id="text"
          name="text"
          class="form-control"
          placeholder="Caption"
          v-model='text'
        ></textarea>
        <br />
        <label for="image">Image:</label>
        <input type="file" id="image" ref="image" @change="uploadImage"/>
        <br />
      </div>
      <div align="center">
        <button type="submit" class="btn btn-lg btn-primary">Post</button>
      </div>
    </form>
    <br />
    <div align="center">
      <a href="/"
        ><button type="button" class="btn btn-lg btn-secondary">Back</button></a
      >
    </div>
  </div>
</template>

<script>
import axios from 'axios'
export default {
    name: 'CreatePost',
    data() {
    return { 
        title:'', 
        text:'',
        image:null
      }
    },
    methods: {
    async create_post() {
      const formData = new FormData();
      formData.append("title", this.title);
      formData.append("text", this.text);
      formData.append("image", this.image);
      try {
        const response = await axios.post("/create-post", formData,{
            headers: {
            Authorization: 'Bearer ' + localStorage.getItem('access_token')
        }
        });
        if (response.data.status === "success") {
            alert(response.data.message);
          this.$router.push("/");
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
}
</script>