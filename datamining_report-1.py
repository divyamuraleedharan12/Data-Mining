# -*- coding: utf-8 -*-
"""DataMining_Report

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1eAyN0VgcNYTHF5mvGKKIo20jVoehi17v
"""

# Import necessary libraries
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.cm as cm
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix,f1_score
from sklearn.preprocessing import StandardScaler, label_binarize
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from prettytable import PrettyTable
from sklearn.metrics import roc_curve, auc
from sklearn.feature_selection import SelectFromModel

# Get the features from the file features.txt
features = list()
features = [line.split()[1] for line in open('/content/features.txt')]
print('No of Features: {}'.format(len(features)))

"""**Getting Train data**

---


"""

# Get train data from txt file to pandas dataframe
X_train = pd.read_csv('/content/X_train.txt', \
                      delim_whitespace=True, header=None)
X_train.columns = [features]
# Adding subject column to the dataframe
X_train['subject'] = pd.read_csv('/content/subject_train.txt', \
                                 header=None)
y_train = pd.read_csv('/content/y_train.txt', names=['Activity'])
y_train_labels = y_train['Activity'].map({1: 'WALKING', 2:'WALKING_UPSTAIRS',3:'WALKING_DOWNSTAIRS',\
                       4:'SITTING', 5:'STANDING',6:'LAYING'})
# Concatenate features X_train and activity labels y_train_labels
train = pd.concat([X_train, y_train_labels], axis=1)
# Combine MultiIndex columns into a single-level Index
train.columns = train.columns.map(''.join)
# Remove '()' from column names in train data
train.columns = [col.replace('(', '').replace(')', '') for col in train.columns]
train.sample(2)

"""**Getting Test data**

---


"""

# Reading test features, subjects and activity labels
X_test = pd.read_csv('/content/X_test.txt', delim_whitespace=True, header=None)
X_test.columns = [features]
X_test['subject'] = pd.read_csv('/content/subject_test.txt', header=None)
y_test = pd.read_csv('/content/y_test.txt', names=['Activity'])
# Map numerical activity labels to corresponding names
y_test_labels = y_test['Activity'].map({1: 'WALKING', 2: 'WALKING_UPSTAIRS', 3: 'WALKING_DOWNSTAIRS',\
                                        4: 'SITTING', 5: 'STANDING', 6: 'LAYING'})
# Concatenate features X_test and the mapped activity labels
test = pd.concat([X_test, y_test_labels], axis=1)
# Convert MultiIndex columns to a single-level Index and then to strings
test.columns = test.columns.map(''.join)
# Remove '()' from column names in test data
test.columns = [col.replace('(', '').replace(')', '') for col in test.columns]
test.sample(2)

train.shape

test.shape

"""**Data Cleaning**

---


"""

# Checking for duplicates in train data and test data
print('Duplicates in train data: {}'.format(sum(train.duplicated())))
print('Duplicates in test data : {}'.format(sum(test.duplicated())))

# Checking for null values in train and test data
print('Null values in train: {}'.format(train.isnull().values.sum()))
print('Null values in test : {}'.format(test.isnull().values.sum()))

# Save this dataframe in a csv files
train.to_csv('train.csv', index=False)
test.to_csv('test.csv', index=False)

print(train['Activity'])

print(test['Activity'])

# Checking the unique values in the "Activity" column
print(train.columns)
print(train['Activity'].unique())

# Check the data type of the "Activity" column
print(train['Activity'].dtype)

# Plotting graph for Distribution of Activities by User
plt.figure(figsize=(8,8))
plt.title('Data provided by each user', fontsize=20)
sns.countplot(x='subject', hue='Activity', data=train, palette='muted')
plt.savefig('fig1_data_each_user.png')
plt.show()

# Plotting graph for Distribution of Datapoints Across Activities
plt.figure(figsize=(12, 8), tight_layout=True)
plt.title('No of Datapoints per Activity', fontsize=15)
sns.countplot(x='Activity', data=train, palette="Blues")
plt.xticks(rotation=30)
plt.savefig('fig2_no_of_datapoints.png', dpi=300)
plt.show()

"""**Data Analysis**

---


"""

# Obtaining train and test data
train = pd.read_csv('train.csv')
test = pd.read_csv('test.csv')
# Checking the shape of train and test data
print(train.shape, test.shape)

# Use the selected features for scaling
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Feature selection using Random Forest Classifier
Rtree_clf = RandomForestClassifier()
Rtree_clf.fit(X_train_scaled, y_train.values.ravel())
# Use SelectFromModel to get selected features
model = SelectFromModel(Rtree_clf, prefit=True)
X_train_selected = model.transform(X_train_scaled)
X_test_selected = model.transform(X_test_scaled)

"""**Naive Bayes Classifier**"""

# Naive Bayes Classifier
nb_classifier = GaussianNB()
nb_classifier.fit(X_train_selected, y_train.values.ravel())
y_pred_nb = nb_classifier.predict(X_test_selected)

"""**Decision Tree Classifier**"""

# Decision Tree Classifier
decision_tree = DecisionTreeClassifier()
decision_tree.fit(X_train_selected, y_train)
y_pred_dt = decision_tree.predict(X_test_selected)

"""**Random Forest Classifier**"""

# Random Forest Classifier
random_forest = RandomForestClassifier()
random_forest.fit(X_train_selected, y_train.values.ravel())
y_pred_rf = random_forest.predict(X_test_selected)

"""**Model Evaluation and Visualization**

---


"""

# Function to plot confusion matrix
def plot_conf_matrix(y_true, y_pred, model_name, activity_labels):
    # Computing the confusion matrix
    matrix = confusion_matrix(y_true, y_pred)
    plt.figure(figsize=(12,8))
    # Plotting the confusion matrix as a heatmap
    sns.heatmap(matrix, annot=True, fmt="d", cmap="Blues",
                xticklabels=activity_labels, yticklabels=activity_labels)
    plt.title(f'Confusion Matrix - {model_name}')
    plt.xlabel('Predicted label')
    plt.ylabel('Actual label')
    plt.xticks(rotation=10)
    plt.yticks(rotation=0)
    plt.tight_layout()
    plt.savefig(f'{model_name}_confusion_matrix.png',dpi=300)  # Saving the figure as an image
    plt.show()

# Function to print results in a table
def print_results(model_name, classification_rep, save_path=None):
    table = PrettyTable()
    table.field_names = ["Model Name", "Metric", "Value"]
    # Adding row to the table
    table.add_row([model_name, "Classification Report", f"\n{classification_rep}"])
    # Displaying the title
    print(f"Results for {model_name}\n")
    print(table)

# Function to plot ROC curve
def plot_roc_curve(y_test, y_pred_prob, classes, model_name):
    # Create a figure for the ROC curve plot
    plt.figure(figsize=(12,8))
    # Plot the ROC curve with AUC label for each class
    for i in range(len(classes)):
        fpr, tpr, thresholds = roc_curve(y_test == classes[i], y_pred_prob[:, i])
        roc_auc = auc(fpr, tpr)
        plt.plot(fpr, tpr, lw=2, label=f'Class {classes[i]} (AUC = {roc_auc:.2f})', color='darkorange')
    # Add a diagonal reference line
    plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
    # Set x and y axis limits
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    # Set axis labels and title
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title(f"Receiver Operating Characteristic (ROC) - {model_name}")
    # Display grid
    plt.grid(True)
    # Add legend in the lower right corner
    plt.legend(loc='lower right')
    plt.savefig(f'{model_name}_roc_curve.png', dpi=300)
    # Show the ROC curve plot
    plt.show()

# Model Evaluation/ Classification Report
def model_evaluate(model, X_test_scaled, y_test, model_name, activity_labels):
    y_pred = model.predict(X_test_scaled)

    # Mapping labels in y_test and y_pred
    y_test_labels = y_test['Activity'].map({1: 'WALKING', 2: 'WALKING_UPSTAIRS', 3: 'WALKING_DOWNSTAIRS',
                                            4: 'SITTING', 5: 'STANDING', 6: 'LAYING'})
    y_pred_labels = pd.Series(y_pred).map({1: 'WALKING', 2: 'WALKING_UPSTAIRS', 3: 'WALKING_DOWNSTAIRS',
                                           4: 'SITTING', 5: 'STANDING', 6: 'LAYING'})

    classification_rep = classification_report(y_test_labels, y_pred_labels, target_names=activity_labels)
    print_results(model_name, classification_rep)

# Print results for each model
activity_labels = ['WALKING', 'WALKING_UPSTAIRS', 'WALKING_DOWNSTAIRS', 'SITTING', 'STANDING', 'LAYING']
model_evaluate(nb_classifier, X_test_selected, y_test, "Naive Bayes", activity_labels)
plot_conf_matrix(y_test, y_pred_nb, "Naive Bayes", activity_labels=activity_labels)
model_evaluate(decision_tree, X_test_selected, y_test, "Decision Tree", activity_labels)
plot_conf_matrix(y_test, y_pred_dt, "Decision Tree", activity_labels=activity_labels)
model_evaluate(random_forest, X_test_selected, y_test, "Random Forest", activity_labels)
plot_conf_matrix(y_test, y_pred_rf, "Random Forest", activity_labels=activity_labels)

# Call the function to plot ROC curve for Naive Bayes
plot_roc_curve(y_test, nb_classifier.predict_proba(X_test_selected),\
                          classes=np.unique(y_train), model_name="Naive Bayes")

# Call the function to plot ROC curve for Decision Tree
plot_roc_curve(y_test, decision_tree.predict_proba(X_test_selected),\
                          classes=np.unique(y_train), model_name="Decision Tree")

# Call the function to plot ROC curve for Random Forest
plot_roc_curve(y_test, random_forest.predict_proba(X_test_selected),\
                          classes=np.unique(y_train), model_name="Random Forest")

"""**Comparing Models**"""

# Function to print results in a table for all models
def print_comparison_table(model_names, accuracies, errors, f1_scores):
    table = PrettyTable()
    table.field_names = ["Model Name", "Accuracy", "Error", "F1 Score"]
    # Displaying the title
    print("Comparing Models")
    # Add rows to the table for all models
    for model_name, accuracy, error, f1_score in zip(model_names, accuracies, errors, f1_scores):
        table.add_row([model_name, f"{accuracy:.2%}", f"{error:.2%}", f"{f1_score:.2%}"])
    # Print the table
    print(table)

# Function to compare models and print a table for all models
def compare_all_models(nb_classifier, decision_tree, random_forest, X_test_scaled, y_test):
    model_names = ["Naive Bayes", "Decision Tree", "Random Forest"]
    models = [nb_classifier, decision_tree, random_forest]
    accuracies, errors, f1_scores = [], [], []
    # Evaluate each model and collect performance metrics
    for model, model_name in zip(models, model_names):
        y_pred = model.predict(X_test_scaled)
        accuracy = accuracy_score(y_test, y_pred)
        error = 1 - accuracy
        f1 = f1_score(y_test, y_pred, average='weighted')
        accuracies.append(accuracy)
        errors.append(error)
        f1_scores.append(f1)

    # Print the comparison table for all models
    print_comparison_table(model_names, accuracies, errors, f1_scores)

# Call the function to compare all models
compare_all_models(nb_classifier, decision_tree, random_forest, X_test_selected, y_test)