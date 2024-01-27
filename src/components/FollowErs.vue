<template>
    <div>
      <div v-if="usernames.length > 0">
        <h1>{{ username }} is being followed by:</h1>
        <div v-for="usern in usernames" :key="usern" class="mt-4 container-fluid border">
          <router-link :to="'/dashboard/' + usern"><h2 class="text-dark">{{ usern }}</h2></router-link>
        </div>
      </div>
      <div v-else>
        <h2 class="text-dark">No one is following {{ username }}</h2>
      </div>
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
    usernames:[]
    }
},
props: {
    username: {
    type: String,
    required: true
    }
},
mounted() {
    const headers = {
        Authorization: 'Bearer ' + localStorage.getItem('access_token'),
        };
    axios.get(`/followers/${this.username}`, { headers })
    .then(response => {
        this.usernames= response.data.usernames;
    })
    .catch(error => {
        console.error(error);
    })
}
}
</script>