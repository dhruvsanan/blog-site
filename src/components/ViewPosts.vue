<template>
    <div class="container mt-5">
        <div v-for="post in posts" :key="post.id">
            <div id="posts">
                <div class="card border-dark">
                    <div class="card-header d-flex justify-content-between align-items-center">
                        <a v-bind:href="'/dashboard/' + post.username">{{ post.username }}</a>
                    <div>
                        Likes:{{ post.like }}
                    </div>
                    </div>
                        <div class="card-body">
                            <a v-bind:href="'/post/' + post.id">
                                <h4 class="card-title">{{ post.title }}</h4>
                            </a>
                            <br />
                            <p class="card-text">{{ post.text }}</p>
                            <br />
                            <template v-if="post.url">
                                <img :src="`http://127.0.0.1:5000${post.url}`" class="img-fluid">
                                <br />
                            </template>
                        </div>
                    </div>
                </div>
        </div>
    </div>
</template>

<script>
import axios from 'axios'
export default {
    name: 'PostsPage',
    props: {
      username: {
        type: String,
        required: true
      }
    },
    data(){
        return {
            posts:[],
        }
    },
    async mounted() {
        try {
            const response = await axios.get(`/api/posts/${this.username}`, {
                headers: {
                    Authorization: 'Bearer ' + localStorage.getItem('access_token'),
                    "Content-Type" : "application/json"
                }
            })
            this.posts = response.data
        } catch(error) {
            console.log(error)
        }

    }
}
</script>

<style>
.link-style {
    font-weight:bold;
    color:black;
    text-decoration:none;
}
.link-style:hover {
    color:grey;
    text-decoration:none;
}
</style>
