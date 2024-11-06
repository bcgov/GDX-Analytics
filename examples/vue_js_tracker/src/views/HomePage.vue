<template>
    <div class="home">
      <img alt="Vue logo" src="../assets/logo.png" />
      <h1>Welcome to Vue 3.js Snowplow Tracker Test Page!</h1>
      This is an example of a two page Vue.js app. It has the Snowplow Javascript Standalone web tracker vE.2.14.0 Installed.
      Click the links to activate more Snowplow events.
    </div>
  </template>
  
  <script>
  export default {
    name: 'HomePage'
  }
  </script>
  
  <style scoped>
  .home {
    text-align: center;
  }
  
  img {
    width: 200px;
  }
  </style>