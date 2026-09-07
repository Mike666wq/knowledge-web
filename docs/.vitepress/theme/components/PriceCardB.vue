<script setup>
// 定价卡 B（Uiverse $251 卡）：黑色圆角 + 6 条勾选特性 + 圆角 Get started 按钮
</script>

<template>
  <div class="pcard">
    <p class="pcard__price">$ 251</p>
    <ul class="pcard__list">
      <li class="pcard__item">
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><path fill="#ffffff" d="M21.5821 5.54289C21.9726 5.93342 21.9726 6.56658 21.5821 6.95711L10.2526 18.2867C9.86452 18.6747 9.23627 18.6775 8.84475 18.293L2.29929 11.8644C1.90527 11.4774 1.89956 10.8443 2.28655 10.4503C2.67354 10.0562 3.30668 10.0505 3.70071 10.4375L9.53911 16.1717L20.1679 5.54289C20.5584 5.15237 21.1916 5.15237 21.5821 5.54289Z" clip-rule="evenodd" fill-rule="evenodd"></path></svg>
        <span>Connect 80 websites</span>
      </li>
      <li class="pcard__item">
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><path fill="#ffffff" d="M21.5821 5.54289C21.9726 5.93342 21.9726 6.56658 21.5821 6.95711L10.2526 18.2867C9.86452 18.6747 9.23627 18.6775 8.84475 18.293L2.29929 11.8644C1.90527 11.4774 1.89956 10.8443 2.28655 10.4503C2.67354 10.0562 3.30668 10.0505 3.70071 10.4375L9.53911 16.1717L20.1679 5.54289C20.5584 5.15237 21.1916 5.15237 21.5821 5.54289Z" clip-rule="evenodd" fill-rule="evenodd"></path></svg>
        <span>Connect up to 5 bank accounts</span>
      </li>
      <li class="pcard__item">
        <svg xmlns="http://www3.org/2000/svg" fill="none" viewBox="0 0 24 24"><path fill="#ffffff" d="M21.5821 5.54289C21.9726 5.93342 21.9726 6.56658 21.5821 6.95711L10.2526 18.2867C9.86452 18.6747 9.23627 18.6775 8.84475 18.293L2.29929 11.8644C1.90527 11.4774 1.89956 10.8443 2.28655 10.4503C2.67354 10.0562 3.30668 10.0505 3.70071 10.4375L9.53911 16.1717L20.1679 5.54289C20.5584 5.15237 21.1916 5.15237 21.5821 5.54289Z" clip-rule="evenodd" fill-rule="evenodd"></path></svg>
        <span>Track up to 50 credit cards</span>
      </li>
      <li class="pcard__item">
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><path fill="#ffffff" d="M21.5821 5.54289C21.9726 5.93342 21.9726 6.56658 21.5821 6.95711L10.2526 18.2867C9.86452 18.6747 9.23627 18.6775 8.84475 18.293L2.29929 11.8644C1.90527 11.4774 1.89956 10.8443 2.28655 10.4503C2.67354 10.0562 3.30668 10.0505 3.70071 10.4375L9.53911 16.1717L20.1679 5.54289C20.5584 5.15237 21.1916 5.15237 21.5821 5.54289Z" clip-rule="evenodd" fill-rule="evenodd"></path></svg>
        <span>Analytics support</span>
      </li>
      <li class="pcard__item">
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><path fill="#ffffff" d="M21.5821 5.54289C21.9726 5.93342 21.9726 6.56658 21.5821 6.95711L10.2526 18.2867C9.86452 18.6747 9.23627 18.6775 8.84475 18.293L2.29929 11.8644C1.90527 11.4774 1.89956 10.8443 2.28655 10.4503C2.67354 10.0562 3.30668 10.0505 3.70071 10.4375L9.53911 16.1717L20.1679 5.54289C20.5584 5.15237 21.1916 5.15237 21.5821 5.54289Z" clip-rule="evenodd" fill-rule="evenodd"></path></svg>
        <span>Export up to 12 months data</span>
      </li>
      <li class="pcard__item">
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><path fill="#ffffff" d="M21.5821 5.54289C21.9726 5.93342 21.9726 6.56658 21.5821 6.95711L10.2526 18.2867C9.86452 18.6747 9.23627 18.6775 8.84475 18.293L2.29929 11.8644C1.90527 11.4774 1.89956 10.8443 2.28655 10.4503C2.67354 10.0562 3.30668 10.0505 3.70071 10.4375L9.53911 16.1717L20.1679 5.54289C20.5584 5.15237 21.1916 5.15237 21.5821 5.54289Z" clip-rule="evenodd" fill-rule="evenodd"></path></svg>
        <span>Cloud service 24/7</span>
      </li>
    </ul>
    <a href="#" class="pcard__action">Get started</a>
  </div>
</template>

<style scoped>
.pcard {
  max-width: 320px;
  display: flex;
  flex-direction: column;
  border-radius: 1.5rem;
  background-color: #000;
  color: #fff;
  padding: 1.5rem;
  box-shadow: 0 0 25px rgba(0, 0, 0, 0.3);
  margin: 0 auto;
  box-sizing: border-box;
}
.pcard__price {
  font-size: 3rem;
  line-height: 1;
  font-weight: 600;
  margin: 0;
}
.pcard__list {
  margin: 2.5rem 0 0;
  padding: 0;
  list-style: none;
  display: flex;
  flex-direction: column;
  row-gap: 0.75rem;
  font-size: 0.875rem;
  color: #fff;
}
.pcard__item { display: flex; align-items: center; }
.pcard__item svg { height: 1rem; width: 1rem; flex-shrink: 0; }
.pcard__item span { margin-left: 1rem; }
.pcard__action {
  margin-top: 2rem;
  display: block;
  width: 100%;
  border: 2px solid #fff;
  border-radius: 9999px;
  background-color: #fff;
  padding: 0.625rem 1.5rem;
  font-weight: 600;
  text-align: center;
  font-size: 0.875rem;
  color: #000;
  text-decoration: none;
  transition: all 0.2s ease;
  box-sizing: border-box;
}
.pcard__action:hover { color: #fff; background-color: transparent; }
</style>
