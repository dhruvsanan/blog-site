<template>
    <div>
      <button @click="celery_job">Download Demo data</button>
      <form @submit.prevent="submitForm">
        <br />
        <label for="csv_file">CSV File:</label>
        <input type="file" id="csv_file" ref="csv_file" />
        <br />
        <button type="submit">Submit</button>
      </form>
    </div>
</template>

<script>
import axios from 'axios'
export default {
data() {
    return {
    }
},
methods: {celery_job: function () {
      fetch("http://localhost:5000/import-demo-csv",{
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
      },
    async submitForm() {
    const csvFile = this.$refs.csv_file.files[0];
    const formData = new FormData();
    formData.append('csv_file', csvFile);
    try {
        const response = await axios.post("/create-posts-from-csv", formData,{
            headers: {
            Authorization: 'Bearer ' + localStorage.getItem('access_token')
        }
        });
        if (response.data === "Task triggered") {
          this.$router.push("/");
        } else {
          console.log(response.data);
        }
      } catch (error) {
        console.error(error);
        alert("An error occurred, please try again.");
      }
    }
}
}
</script>