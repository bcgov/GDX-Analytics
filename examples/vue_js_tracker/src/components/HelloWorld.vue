<template>
  <div class="hello">
    <h1>{{ msg }}</h1>
    <div style="font-weight: bold;">
    <p>
    This site uses a Navigation Guard provided by the Router module. It calls a Global After Hook to call the 
    Snowplow Page Tracker function. 
    </p>
    <p>
    For more information on this technique, see the Vue.js documentation on this method, here:
    </p>
    <p>
    <a href="https://router.vuejs.org/guide/advanced/navigation-guards.html#global-after-hooks">
    https://router.vuejs.org/guide/advanced/navigation-guards.html#global-after-hooks
    </a>
    </p>
    </div>

    <div style="padding-top: 125px;">
    <p>
      For a guide and recipes on how to configure / customize a Vue.js project,<br>
      check out the
      <a href="https://cli.vuejs.org" target="_blank" rel="noopener">vue-cli documentation</a>.
    </p>
    <h3>Installed CLI Plugins</h3>
    <ul>
      <li><a href="https://github.com/vuejs/vue-cli/tree/dev/packages/%40vue/cli-plugin-router" target="_blank" rel="noopener">router</a></li>
    </ul>
    
    
  </div>
  </div>
</template>

<script>
export default {
  name: 'HelloWorld',
  props: {
    msg: String
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
h3 {
  margin: 40px 0 0;
}
ul {
  list-style-type: none;
  padding: 0;
}
li {
  display: inline-block;
  margin: 0 10px;
}
a {
  color: #42b983;
}
</style>
