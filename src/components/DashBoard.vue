<template>
<div class="container p-3 my-3">
    <div class="row">
    <div class="col-md-9 col-sm-12">
        <br>
        <h1>Welcome to {{username}}'s dashboard!</h1>
        <br>
        <p>Here you can see about {{username}}.</p>
        <br>
        <div class="row">
        <div class="col-md-4 col-sm-6">
            <div class="card bg-light p-3 my-3">
              <div class="card-header">Account Information</div>
              <div class="card-body">
                <p class="card-text">Name: {{username}}</p>
                <p class="card-text">Email: {{email}}</p>
                <br />
                <label for="image">Profile Picture:</label><br>
                <p v-if="!url" class="card-text">{{username}} has no Profile Picture</p>
                <img v-else :src="`http://127.0.0.1:5000${url}`" class="img-fluid">
                <br />
                <button @click="trigger_celery_job">Download Your CSV data</button>
                <button @click="sendReport">Send Report</button>
                <button @click="dailyReminder">Daily Reminder</button>
              </div>
            </div>
            <div class="card bg-light p-3 my-3">
              <h5> Set Time for reminder</h5>
              <form>
                <label>
                  Hour of day:
                  <input type="number" v-model="hour" min="0" max="23" required>
                </label>
                <br>
                <label>
                  minute of hour:
                  <input type="number" v-model="minute" min="0" max="59" required>
                </label>
                <br>
                <form @submit.prevent="setDailyTimeFrame">
                <button type="submit">Set Daily Time Frame</button>
                </form>
                <br>
                <form @submit.prevent="setMonthlyTimeFrame">
                <button type="submit">Set Monthly Time Frame</button>
                <br>
                <br>
                <form>
                  <input type="radio" name="format" value="html" v-model="selectedFormat"> HTML
                  <input type="radio" name="format" value="pdf" v-model="selectedFormat"> PDF
                  <br>
                  <button @click.prevent="exportData" type="submit">Monthly Email Format</button>
                </form>
                </form>
            </form>
            </div>
            <div class="card bg-light p-3 my-3">
            <div class="card-header">Follow Information</div>
            <div class="card-body">
                <p class="card-text">Total number of Followers: {{nfollows}}</p>
                <p class="card-text">Total number of Following: {{nfollowed}}</p>
                <template v-if="user.sub !== uid">
                    <button v-if="userfollowing" @click="unfollow" class="btn btn-danger">Unfollow</button>
                    <button v-else @click="follow" class="btn btn-primary">Follow</button>
                </template>
            </div>
            </div>
        </div>
        <div class="col-md-4 col-sm-6">
            <div class="card bg-light p-3 my-3">
            <div class="card-header">Posts Information</div>
            <div class="card-body">
              <div class="card-header"><router-link :to="{ path: '/mychart/' }">View Post Engagement</router-link></div>
                <div class="card-header"><router-link :to="{ path: '/posts/' + username }">View Posts</router-link></div>
                <template v-if="user.sub === uid">
                <div class="card-header">
                </div>
                </template>
            </div>
            </div>
        </div>
        <template v-if="user.sub === uid">
            <div class="col-md-4 col-sm-6">
                <div class="card bg-light p-3 my-3">
                <div class="card-header"><router-link to="/updateuser">Update Profile</router-link></div>
                <div class="card-header"><router-link to="/updatepicture">Update Profile Picture</router-link></div>
                <div class="card-header"><router-link to="/updatepassword">Update Password</router-link></div>
                <div class="card-header"><button type="submit" @click="deleteUser()">Delete your Id</button></div>
                </div>
            </div>
        </template>
        <div class="col-md-4 col-sm-6">
            <div class="card bg-light p-3 my-3">
            <div class="card-header"><router-link :to="{ path: '/followers/' + username }">followers</router-link></div>
            <div class="card-header"><router-link :to="{ path: '/following/' + username }">following</router-link></div>
            </div>
        </div>
    </div>
    </div>
    </div>
    <div align="center">
    <router-link to="/">
        <button type="button" class="btn btn-primary btn-lg">Back</button>
    </router-link>
    </div>
</div>
</template>
<script>
import jwtDecode from 'jwt-decode'
import axios from 'axios'
  export default {
    name: 'DashBoard',
    props: {
      username: {
        type: String,
        required: true
      }
    },
    data() {
      return {
        nfollows: '',
        nfollowed: '',
        following: '',
        followings: '',
        nposts: '',
        ncomments: '',
        views: '',
        url: '',
        email:'',
        uid:'',
        userfollowing:'',
        user:null,
        selectedFormat:'',
        minute:'',
        hour:'',

      }
    },
    methods: {
      async setMonthlyTimeFrame() {
      try {
         await axios.get('/set-month-time', {
          params: { minute: this.minute,
            hour:this.hour
           },
          headers: {
            Authorization: 'Bearer ' + localStorage.getItem('access_token'),
            "Content-Type": "application/json"
          }
        })
        console.log('POST request successful')
        this.hour=''
        this.minute=''
      } catch (error) {
        console.error('GET request failed:', error)
      }
    },async setDailyTimeFrame() {
      try {
         await axios.get('/set-daily-time', {
          params: { hour: this.hour,
            minute:this.minute
           },
          headers: {
            Authorization: 'Bearer ' + localStorage.getItem('access_token'),
            "Content-Type": "application/json"
          }
        })
        console.log('POST request successful')
        this.hour=''
        this.minute=''
      } catch (error) {
        console.error('GET request failed:', error)
      }
    },
    sendReport() {
      axios.get('http://127.0.0.1:5000/send-report', {
        headers: {
          Authorization: 'Bearer ' + localStorage.getItem('access_token'),
          "Content-Type": "application/json"
        }
      })
    },
    dailyReminder() {
      axios.get('http://127.0.0.1:5000/daily-reminder', {
        headers: {
          Authorization: 'Bearer ' + localStorage.getItem('access_token'),
          "Content-Type": "application/json"
        }
      })
    },
    async exportData() {
      try {
        await axios.get('/set-monthly-format', {
          params: { selectedFormat: this.selectedFormat},
          headers: {
            Authorization: 'Bearer ' + localStorage.getItem('access_token'),
            "Content-Type": "application/json"
          }
        })
        console.log('POST request successful')
        this.selectedFormat = null
      } catch (error) {
        console.error('GET request failed:', error)
      }
    },
      follow() {
        const headers = {
        Authorization: 'Bearer ' + localStorage.getItem('access_token'),
        };
        axios.post(`/follow/${this.username}`, {}, { headers })
          .then(response => {
            alert(response.data.message);
            this.userfollowing=true;
            this.nfollows ++
          })
          .catch(error => console.log(error))
      },
      unfollow() {
        const headers = {
        Authorization: 'Bearer ' + localStorage.getItem('access_token'),
        };
        axios.post(`/follow/${this.username}`, {}, { headers })
          .then(response => {
            alert(response.data.message);
            this.userfollowing=false;
            this.nfollows --
          })
          .catch(error => console.log(error))
      },
      async deleteUser() {
      try {
        const response = await axios.post("/delete-user", {}, {
          headers: {
            Authorization: "Bearer " + localStorage.getItem("access_token"),
          },
        });
        this.$router.push(`/signup`);
        console.log(response.data); // Handle the response data
      } catch (error) {
        console.log(error.response.data); // Handle the error response data
      }
    },
    trigger_celery_job: function () {
      fetch("http://localhost:5000/celery-job",{
        headers: {
            Authorization: 'Bearer ' + localStorage.getItem('access_token'),
        "Content-Type" : "application/json"
        }
        })
        .then(r => r.json())
        .then(d => {
        console.log("task details:", d)
        window.location.href= "http://localhost:5000/download-file"
        })
        .catch(error => {
        console.error("Error occurred:", error);
      });
      }
    },
    mounted() {
      axios.get(`/dashboard/${this.username}`,{
        headers: {
            Authorization: 'Bearer ' + localStorage.getItem('access_token'),
        }
      })
    //   .then(response => console.log(response))
        .then(response => {
          const data = response.data
          this.nfollows = data.nfollows
          this.nfollowed = data.nfollowed
          this.following = data.following
          this.followings = data.followings
          this.nposts = data.nposts
          this.ncomments = data.ncomments
          this.views = data.views
          this.url = data.url
          this.email=data.email
          this.uid=data.uid,
          this.userfollowing=data.userfollowing
        })
        .catch(error => console.log(error))
    },
    created(){
        const token = localStorage.getItem('access_token')
        if (token) {
            this.user = jwtDecode(token)
            console.log(this.user.sub)
    }
    }
  }
</script>