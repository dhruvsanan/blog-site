<template>
    <div>
      <div v-if="users">
        <h2>Search Results:</h2>
        <ul>
          <li v-for="user in users" :key="user.username">
            <a :href="`/dashboard/${user.username}`">{{ user.username }}</a>
          </li>
        </ul>
      </div>
      <div v-else>
        <h2> no user found</h2>
      </div>
    </div>
</template>

<script>
import axios from 'axios'

export default {
  props: ['username'],
  data() {
    return {
      users: null
    }
  },
  async created() {
    console.log('created hook called')
    console.log('username prop:', this.username)
    if (this.username) {
      console.log('sending GET request to /search-user')
      try {
        const response = await axios.get('/search-user', {
          params: { name: this.username },
          headers: {
            Authorization: 'Bearer ' + localStorage.getItem('access_token'),
            "Content-Type": "application/json"
          }
        })
        console.log('GET request successful')
        this.users = response.data.users
      } catch (error) {
        console.error('GET request failed:', error)
      }
    } else {
      console.log('username prop is falsy')
    }
  }
}
</script>