<template>
  <div v-if="!consentGiven" class="cookie-banner">
    <p>We use cookies to enhance your experience. By continuing to visit this site you agree to our use of cookies.</p>
    <button @click="giveConsent">Accept</button>
  </div>
</template>

<script>
export default {
  data() {
    return {
      consentGiven: this.getConsent()
    };
  },
  methods: {
    giveConsent() {
      // Set consent to true in the local storage
      localStorage.setItem('cookieConsent', 'true');
      this.consentGiven = true;
    },
    getConsent() {
      // Check if consent has already been given
      return localStorage.getItem('cookieConsent') === 'true';
    }
  }
};
</script>

<style scoped>
.cookie-banner {
  position: fixed;
  bottom: 0;
  width: 100%;
  background-color: #f5f5f5;
  padding: 20px;
  text-align: center;
  border-top: 1px solid #ccc;
}
</style>
