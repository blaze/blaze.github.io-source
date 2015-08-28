Title: Examples
Category: Examples



<section class="home-section">
    <h2 class="home-header">Examples</h2>
    <div class="row">
      {% for page in pages %}
          {% if page.title == 'Examples' %}
              {% for children_page in page.children[0:2] %}
              <div class="one-half column">
                  <a class="screenshot-wrapper" target="_blank" href="{{ SITEURL }}/{{ children_page.url }}">
                     <img class="screenshot" src="{{ SITEURL }}/images/{{ children_page.image }}">
                  </a>
                  <h5 class="talk-header"><a href="{{ SITEURL }}/{{ children_page.url }}">{{ children_page.title }}</a></h5>
              </div>
              {% endfor %}
          {% endif %}
      {% endfor %}
    </div>
</section>