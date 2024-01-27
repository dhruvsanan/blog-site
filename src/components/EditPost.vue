<template>
  <div class="container mt-4">
    <h1 align="center">Update the Post</h1>
    <form @submit.prevent="edit_post">
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
        <img :src="`http://127.0.0.1:5000${url}`" class="img-fluid">
        <input type="file" id="image" ref="image" @change="uploadImage"/>
        <br />
      </div>
      <div align="center">
        <button type="submit" class="btn btn-lg btn-primary">Post</button>
      </div>
    </form>
    <br />
    <div align="center">
      <a :href="`/post/${id}`">
        <button type="button" class="btn btn-lg btn-secondary">Back</button>
      </a>
    </div>
  </div>
</template>
  
<script>
import axios from 'axios'
export default {
  name: 'EditPost',
  data() {
    return { 
      title:'', 
      text:'',
      image:null
    }
  },
  props:{
    id: {
      type:[Number,String],
      required:true
    }
  },
  methods: {
    async edit_post() {
      const formData = new FormData();
      formData.append("title", this.title);
      formData.append("text", this.text);
      formData.append("image", this.image);
      try {
        const response = await axios.put(`/update-post/${this.id}`, formData,{
          headers: {
            Authorization: 'Bearer ' + localStorage.getItem('access_token')
          }
        });
        if (response.data.status === "success") {
          alert(response.data.message);
          this.$router.push(`/post/${this.id}`);
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
    fetch(`http://localhost:5000/api/post/${this.id}`,{
      method: "GET",
      headers: {
        Authorization: 'Bearer ' + localStorage.getItem('access_token'),
        "Content-Type" : "application/json"
      }
    })
    .then(resp => resp.json ()) 
    .then(data => {
      this.title = data.title;
      this.text = data.text;
      this.url = data.url;
      console.log(data);
    })
    .catch(error=> {
      console.log(error)
    })
  }
}
</script>

<style>

</style>
