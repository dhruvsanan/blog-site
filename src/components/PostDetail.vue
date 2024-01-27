<template>
    <div id="posts">
      <div class="card border-dark">
        <div class="card-header d-flex justify-content-between align-items-center">
            <a v-bind:href="'/dashboard/' + post.username">{{ post.username }}</a>
          <div>
            {{ post.like }}
            <button @click="likePost">
                <i :class="likeButtonClass"></i>
            </button>
            <template v-if="user.sub === post.author">
                <div>
                        <button class="btn btn-danger mX-3 mt-3" @click.prevent="deletePost($event)">
                                        Delete Post
                                        </button>
                        <a v-bind:href="'/edit/' + post.id" class="btn btn-success mt-3">
                                        Update
                        </a>
                </div>
            </template>
          </div>
        </div>
            <div class="card-body">
                <h4 class="card-title">{{ post.title }}</h4>
                <br />
                <p class="card-text">{{ post.text }}</p>
                <br />
                <template v-if="post.url">
                    <img :src="`http://127.0.0.1:5000${post.url}`" class="img-fluid">
                    <br />
                </template>
            </div>
            <br>
            <template v-if="comments.length > 0" >
                <h3>Comments:</h3>
                <div v-for="comment in comments" :key="comment.id" class="d-flex justify-content-between align-items-center">
                  <div>
                    <h4><router-link :to="'/dashboard/' + comment.username">{{comment.username}}</router-link>: {{comment.text}}</h4>
                  </div>
                  <div>
                    <small class="text-muted"> {{comment.date_created}}</small>
                    <div v-if="user.sub == comment.author || user.sub == post.author" class="btn-group">
                      <button type="button" class="btn btn-sm btn-primary dropdown-toggle" data-bs-toggle="dropdown"></button>
                      <ul class="dropdown-menu">
                        <li><button type="submit" @click.prevent="deleteComment(comment.id)">Delete</button></li>
                        <a :href="`/update-comment/${comment.id}`">
                        <button type="button" @click.prevent="updateComment(comment.id)">Update</button>
                        </a>
                      </ul>
                    </div>
                  </div>
                </div>
            </template>
            <template v-else>
              <h4 class="text-muted">No Comments</h4>
            </template>
            <br>
            <form
            class="input-group mb-3"
            @submit.prevent="createComment(post.id)"
          >
            <input
              type="text"
              v-model="newCommentText"
              class="form-control"
              placeholder="Comment something!"
            />
            <button type="submit" class="btn btn-primary">Comment</button>
          </form>
        </div>
        <div class="card-footer text-muted">{{ post.date_created }}</div>
        <div class="card-footer text-muted">Total views: {{ post.view }}</div>
      <br />
    </div>
</template>

<script>
import jwtDecode from 'jwt-decode'
import axios from 'axios'
export default {
    name: 'PostDetail',
    data(){
            return {
                post:{},
                user:null,
                comments:[],
                newCommentText:'',
                likeButtonClass:''
            }
        },
    props:{
        id: {
            type:[Number,String],
            required:true
        }
    },
    methods: {
        async updateComment(id) {
    const updatedCommentText = prompt("Enter updated comment:");
    try {
      const response = await axios.patch(`/update-comment/${id}`, {
        text: updatedCommentText,
      },{
            headers: {
            Authorization: 'Bearer ' + localStorage.getItem('access_token')
        }
    });
      console.log(response.data.message)
      location.reload();
    } catch (error) {
      console.error(error);
    }
  },
        async createComment() {
      const formData = new FormData();
      formData.append("newCommentText", this.newCommentText);
      try {
        const response = await axios.post(`/create-comment/${this.id}`, formData,{
            headers: {
            Authorization: 'Bearer ' + localStorage.getItem('access_token')
        }
        });
        if (response.data.status === "success") {
            alert(response.data.message);
            this.newCommentText = '';
            const commentResponse = await axios.get(`/api/comment/${this.id}`, {
                headers: {
                    Authorization: 'Bearer ' + localStorage.getItem('access_token')
                }
                });
            if (commentResponse.data.status === "success") {
            this.comments = commentResponse.data.comments;
            this.$set(this.comments);
            } else {
            console.log(commentResponse.data.message);
            location.reload();
            }
        } else {
          alert(response.data.message);
        }
      } catch (error) {
        console.error(error);
        alert("An error occurred, please try again.");
      }
    },
        deletePost() {
        fetch(`http://localhost:5000/api/post/${this.id}`,{
        method: "DELETE",
        headers: {
            Authorization: 'Bearer ' + localStorage.getItem('access_token'),
        "Content-Type" : "application/json"
        }
        })
        .then(() => {
            this.$router.push({
                name:'home'
            })
        })
        .catch(error=> {
            console.log(error)
        })
        },
    async getpost() {
        try {
            const response = await axios.get(`/api/post/${this.id}`, {
                headers: {
                    Authorization: 'Bearer ' + localStorage.getItem('access_token'),
                    "Content-Type" : "application/json"
                }
            })
            this.post=response.data,
            this.likeButtonClass=response.data.likeButtonClass;
            console.log(response.data)
        } catch(error) {
            console.log(error)
        }
        },
        getComment() {
        fetch(`http://localhost:5000/api/comment/${this.id}`,{
        method: "GET",
        headers: {
            Authorization: 'Bearer ' + localStorage.getItem('access_token'),
            "Content-Type" : "application/json"
        }
        })
        .then(resp => resp.json ()) 
        .then(data => {
            this.comments=data,
            console.log(data)
        })
        .catch(error=> {
            console.log(error)
        })
        },
        deleteComment(id) {
        fetch(`http://localhost:5000/delete-comment/${id}`,{
        method: "POST",
        headers: {
            Authorization: 'Bearer ' + localStorage.getItem('access_token'),
        "Content-Type" : "application/json"
        }
        }).then(response => {
            console.log(response)
            location.reload();
        })
        .catch(error=> {
            console.log(error)
        })
        },
        likePost() {
            fetch(`http://localhost:5000/like-post/${this.id}`, {
                method: "GET",
                headers: {
                    Authorization: 'Bearer ' + localStorage.getItem('access_token'),
                    "Content-Type": "application/json"
                }
            })
            .then(response => response.json())
            .then(data => {
                console.log(data);
                this.post.like=data.likes;
                this.likeButtonClass=data.likeButtonClass;

            })
            .catch(error => {
                console.log(error);
            });
        },
    },
    created(){
        const token = localStorage.getItem('access_token')
        if (token) {
            this.user = jwtDecode(token)
            console.log(this.user)
    }
        this.getpost(),
        this.getComment()
    }
    
}
</script>

<style>

</style>