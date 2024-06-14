import React, { useState , useEffect } from "react";
import './App.css';

import Keycloak from "keycloak-js";

const backendAddress = "localhost:5002";

let initOptions = {
  url: 'http://localhost:8080/',
  realm: 'myrealm',
  clientId: 'frontend',
}

let kc = new Keycloak(initOptions);

kc.init({
  onLoad: 'login-required',
  checkLoginIframe: true
}).then((auth) => {
  if (!auth) {
    window.location.reload();
  }
  else {
    console.log(kc.token)
  }
});

function App() {
  const [recipes, setRecipes] = useState([]);

  const [title, setTitle] = useState("");
  const [usedProducts, setUsedProducts] = useState("");
  const [timeForCooking, setTimeForCooking] = useState("");

  useEffect(() => {
    fetchRecipes();
  }, []);

  async function fetchRecipes() {
    try {
      const response = await fetch(`http://${backendAddress}/recipe/all`);
      if (!response.ok) {
        throw new Error('Failed to fetch recipes');
      }
      const data = await response.json();
      setRecipes(data.recipes);
    } catch (error) {
      console.error('Error fetching recipes:', error);
    }
  }

  async function addRecipe(event) {
    event.preventDefault();
  
    const token = kc.token;
  
    try {
      const response = await fetch(`http://${backendAddress}/recipe`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ title, usedProducts, timeForCooking, token})
      });
      if (!response.ok) {
        throw new Error('Failed to add recipe');
      }
      await response.json();
      fetchRecipes();
      setTitle("");
      setUsedProducts("");
      setTimeForCooking("");
    } catch (error) {
      console.error('Error adding recipe:', error);
    }
  }

  function deleteRecipe(id) {
    if (window.confirm('Are you sure you want to delete this note?')) {
      fetch(`http://${backendAddress}/recipe/${id}/${kc.token}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${kc.token}`
        }
      })
      .then(response => {
        if (!response.ok) {
          throw new Error('Failed to delete recipe');
        }
        fetchRecipes();
      })
      .catch(error => console.error('Error:', error));
    }
  }

  return (
    <div className="App">
      <h1>Menu Recipes</h1>
      <form id="recipeInfo" onSubmit={addRecipe}>
        <div>
          <label>Title:</label>
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            required
          />
        </div>
        <div>
          <label>Used Products:</label>
          <input
            type="text"
            value={usedProducts}
            onChange={(e) => setUsedProducts(e.target.value)}
            required
          />
        </div>
        <div>
          <label>Time for Cooking (minutes):</label>
          <input
            type="number"
            value={timeForCooking}
            onChange={(e) => setTimeForCooking(e.target.value)}
            required
          />
        </div>
        <button type="submit">Add recipe</button>
      </form>
      <div>
        <h2>Recipes</h2>
        <ul>
          {recipes.map(recipe => (
            <li key={recipe.id}>
              <strong>{recipe.title}</strong>: {recipe.products} ({recipe.cook_time_in_m} minutes)
              <button onClick={() => deleteRecipe(recipe.id)}>Delete</button>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}

export default App;
