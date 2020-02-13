import { h, Component, render } from 'https://unpkg.com/preact?module'
import htm from 'https://unpkg.com/htm?module'

const html = htm.bind(h)

function Nav() {
  return html`
    <nav class="navbar navbar-expand-md navbar-light fixed-top bg-light">
        <a class="navbar-brand" href="/">/property-app</a>
    </nav>`
}

const app = html`
<div>
    <${Nav} />
    <main role="main" class="container-fluid">
        <p>rendered content</p>
    </main>
    <footer class="footer">
        <div class="container">
            <span class="text-muted">Copyright 2020</span>
        </div>
    </footer>
</div>`

render(app, document.getElementById('app'))