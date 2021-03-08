def person_encode(days_waiting, sex, country, age):
    array = [days_waiting]
    if sex == 'male':
        array.append(0)
    else:
        array.append(1)

    countries = ['Angola', 'Brazil', 'Cabo Verde', 'Canada', 'Central African Republic', 'China', 'France', 'Gabon', 'Gambia', 'Germany', 'India', 'Japan', 'Nepal', 'Philippines', 'Romania', 'Singapore', 'South Korea', 'Vietnam']
    array.extend([int(c == country) for c in countries])

    ages = ['0-9', '0.20-29', '10-19', '20-29', '30-39', '40-49', '50-59', '60-69', '70-79', '80-89', '90-99']
    array.extend([int(a == age) for a in ages])
    return array


print(person_encode(30,'male','Brazil',10))