<script setup>
// 定价卡 A（Uiverse dark starter pack）：$24/mo，4 条特性 + 购买按钮
// 放在 /fun 实验室
</script>

<template>
  <div class="pack">
    <div class="head">
      <p class="title">Starter</p>
      <div class="price">
        <span>$</span>24<span>/mo</span>
      </div>
    </div>
    <ul class="lists">
      <li class="item">
        <span class="dot"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4.5 12.75l6 6 9-13.5"></path></svg></span>
        <p>2 team members</p>
      </li>
      <li class="item">
        <span class="dot"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4.5 12.75l6 6 9-13.5"></path></svg></span>
        <p>100+ components</p>
      </li>
      <li class="item">
        <span class="dot"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4.5 12.75l6 6 9-13.5"></path></svg></span>
        <p>2 month free updates</p>
      </li>
      <li class="item">
        <span class="dot"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4.5 12.75l6 6 9-13.5"></path></svg></span>
        <p>Life time technical support</p>
      </li>
    </ul>
    <div class="btn-wrap">
      <button type="button">Buy Now</button>
    </div>
  </div>
</template>

<style scoped>
.pack {
  position: relative;
  display: flex;
  max-width: 320px;
  flex-direction: column;
  border-radius: 12px;
  background-color: #212121;
  border: 1px solid #fff;
  padding: 1.6rem;
  color: #fff;
  box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
  margin: 0 auto;
}
.head {
  position: relative;
  margin: 0 0 2rem;
  border-bottom: 1px solid #fff;
  padding-bottom: 1rem;
  text-align: center;
}
.title {
  margin: 0;
  font-size: 0.875rem;
  text-transform: uppercase;
  color: #fff;
  letter-spacing: 0.1em;
}
.price {
  margin-top: 10px;
  display: flex;
  justify-content: center;
  align-items: flex-start;
  gap: 4px;
  font-size: 4.5rem;
  line-height: 1;
}
.price span:first-child { margin-top: 10px; font-size: 2.25rem; line-height: 2.5rem; }
.price span:last-child  { align-self: flex-end; font-size: 2.25rem; line-height: 2.5rem; }
.lists { display: flex; flex-direction: column; gap: 8px; list-style: none; margin: 0; padding: 0; }
.item { display: flex; align-items: center; gap: 10px; }
.item .dot {
  border-radius: 50%;
  border: 1px solid rgba(255, 255, 255, 0.24);
  background-color: rgba(255, 255, 255, 0.185);
  height: 30px;
  width: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.item .dot svg { height: 12px; width: 12px; }
.item p { margin: 0; }
.btn-wrap { margin-top: 20px; }
.btn-wrap button {
  display: block;
  width: 100%;
  background-color: #fff;
  padding: 10px 20px;
  text-transform: uppercase;
  color: #000;
  outline: 0;
  border: 0;
  border-radius: 10px;
  font-weight: 600;
  cursor: pointer;
}
</style>
