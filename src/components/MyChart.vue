<template>
  <div :style="{ border: '10px solid black', padding: '20px', marginTop: '100px' }">
    <div v-for="item in data" :key="item.label">
      <div :style="{ borderBottom: '1px solid black' }">{{ item.label }}</div>
      <div :style="{ height: '20px', backgroundColor: 'blue', width: item.value + '%' }"></div>
      <div :style="{ marginBottom: '20px' }">{{ item.value }}</div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      data: [],
    };
  },
  async created() {
    const response = await axios.get('/engagement', {
  headers: {
    'Access-Control-Allow-Origin': '*',
    Authorization: 'Bearer ' + localStorage.getItem('access_token'),
  },
})
    const engagementData = response.data;
    this.data = [
      { label: 'Comments', value: engagementData.ncomments },
      { label: 'Followed', value: engagementData.nfollowed },
      { label: 'Follows', value: engagementData.nfollows },
      { label: 'Posts', value: engagementData.nposts },
      { label: 'Views', value: engagementData.views },
    ];
  },
};
</script>