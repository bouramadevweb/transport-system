from django.shortcuts import render, redirect
from .form import EntrepriseForm, InscriptionUtilisateurForm ,ConnexionForm
from django.contrib.auth import authenticate, login

def ajouter_entreprise(request):
    form = EntrepriseForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('liste_entreprises')  # ou une autre vue après l'enregistrement
    return render(request, 'transport/ajouter_entreprise.html', {'form': form})

def inscription_utilisateur(request):
    if request.method == 'POST':
        form = InscriptionUtilisateurForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login') 
    else:
        form = InscriptionUtilisateurForm()

    return render(request, 'transport/UserInscription.html', {'form': form})


def connexion_utilisateur(request):
    form = ConnexionForm(request.POST or None)
    
    if request.method == 'POST':
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, email=email, password=password)

            if user is not None:
                login(request, user)
                return redirect('dashboard')  # Redirige vers une page après connexion
            else:
                form.add_error(None, "Email ou mot de passe invalide.")

    return render(request, 'transport/connexion.html', {'form': form})
