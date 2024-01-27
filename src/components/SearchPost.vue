<template>
    <div>
      <div v-if="posts">
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
      <div v-else>
        <h2> no post found</h2>
      </div>
    </div>
</template>

<script>
import axios from 'axios'

export default {
  props: ['title'],
  data() {
    return {
        posts:[]
    }
  },
  async created() {
    console.log('created hook called')
    console.log('title prop:', this.title)
    if (this.posts) {
      console.log('sending GET request to /search-post')
      try {
        const response = await axios.get('/search-post', {
          params: { title: this.title },
          headers: {
            Authorization: 'Bearer ' + localStorage.getItem('access_token'),
            "Content-Type": "application/json"
          }
        })
        console.log('GET request successful')
        this.posts = response.data.posts
      } catch (error) {
        console.error('GET request failed:', error)
      }
    } else {
      console.log('title prop is falsy')
    }
  }
}
</script>